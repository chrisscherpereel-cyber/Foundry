# Venture Foundry: Performance & Concurrency Audit

Branch: `perf/concurrency-optimizations` · Target: 30–40 concurrent users on Streamlit Community Cloud

> **What has and hasn't been verified.** These changes were made from a static code review. The
> automated review environment did not allow the app's own code to be executed, so **none of the
> before/after numbers below come from running Venture Foundry itself.** Every figure is labeled as
> one of:
> - **Measured:** an SQLite micro-benchmark that does not use the app.
> - **Estimated:** derived by counting queries in the code.
> - **Not measured.**
>
> Run `pytest -q tests/` and the load-test plan in §6 before merging.

## A. Executive summary

The app's speed problem has one dominant cause. **Each page render re-derives the same facts from the
database hundreds to thousands of times.** Each call opens a new SQLite connection. The sidebar
navigation checks whether each of ~16 tools is locked, active, or reference. Each check rebuilds the
semester schedule and re-walks every earlier round's deliverables and concept answers. The to-do
list and the "Next" strip rebuild the full round checklist up to three more times per click. All of
this work grows with the round number, so the app gets slower as the semester goes on. The cost is
almost all CPU under Python's single interpreter lock (the GIL), and every session shares one server
process. With 30–40 students clicking, the requests queue behind each other.

The audit also found **correctness problems that only appear under concurrency**:

- **Round advances race.** At a scheduled advance time, several students loading at the same moment
  could each advance the round. Each one would charge specialist salaries, apply learning, and send
  round mail again.
- **Spending races.** Two teammates spending credits at the same moment could overwrite each other's
  balance change, or both pass the "enough credits?" check against the same balance.

The largest risk sits outside the code. **All semester data lives in a local SQLite file, and
Community Cloud does not preserve local files across reboots or redeploys.** This is a data-loss risk
that code optimization cannot fix (§F).

## B. Optimization results

| Component | Problem identified | Modification | Measured improvement |
|---|---|---|---|
| Application startup | `init_db()` (schema script + ~12 `PRAGMA table_info` + migrations) ran on **every rerun of every session**; favicon decoded every rerun | Run once per server process via `st.cache_resource` | Not measured (est. 20–40 fewer SQL statements per click) |
| Page loading | Est. ~1,500–3,000 SQLite connections per student click at mid-semester (N+1 recomputation of schedule/checklist/tool gating) | Per-run read cache (`db.run_memo`) on 44 read helpers + `get_schedule`, `outstanding_prior`, `round_checklist` | Not measured. Estimate: repeated reads drop to a few dozen distinct queries per click. Measured cost per avoided query: **≈0.34 ms** (connect+PRAGMA+SELECT+close) |
| Session management | Cache must never leak across users | Cache is thread-local, active only inside the script body, cleared on every commit, and never shared across sessions | Covered by tests (not run) |
| CPU utilization | Same as page loading; `founder_level` read skills/hires 7× each | Memoization; read once | Not measured |
| Memory consumption | No large per-session objects found; leaderboard held full team rows (rosters, join codes) | Shared leaderboard cache keeps only display fields; upload cap 10 MB | Not measured |
| File uploads | Only upload is the class roster (KB-sized), parsed from memory once | No parsing change needed. `server.maxUploadSize = 10` (was 200 MB) | Not measured |
| File downloads | Roster template `.xlsx` rebuilt with openpyxl on every Team Setup rerun | Built once (`st.cache_data`) | Not measured |
| Caching | No `st.cache_*` anywhere; leaderboard recomputed every team's score for every viewer | Leaderboard shared per game/metric/round for 30 s | Not measured |
| Concurrent users | Default rollback journal + 5 s lock timeout → "database is locked" under write bursts; advance and spending races | WAL mode, 30 s busy timeout, `synchronous=NORMAL`; per-game advance lock; atomic spend and usage counters | **Measured (micro-benchmark, 4 writers + 4 readers, 50 ms timeout):** lock errors 50 → 15 with WAL. App-level: not measured |

## C. Code modifications

| File | Change |
|---|---|
| `db.py` | Request-scoped read cache (`begin_request`, `end_request`, `run_memo`, `invalidate_run_cache`). A connection subclass clears the cache on commit. WAL, `synchronous=NORMAL`, 30 s timeout. `adjust_resources` now runs in one `BEGIN IMMEDIATE` transaction. New `increment_team_field`. |
| `logic.py` | Memoized `get_schedule`, `outstanding_prior`, `round_checklist`. New `sync_active_game` with a per-game non-blocking lock. `director_advance` takes the same lock. `_add_usage` increments atomically. `set_build_budget` reads fresh. `founder_level` reads once. |
| `app.py` | Schema and favicon set up once per process. Script body wrapped in `begin_request`/`end_request`. Uses `logic.sync_active_game`. |
| `views_student.py` | Shared 30 s leaderboard cache (display fields only). |
| `views_instructor.py` | Cached roster template bytes. |
| `.streamlit/config.toml` (new) | `maxUploadSize = 10`, `gatherUsageStats = false`. |
| `tests/test_perf_safety.py` (new) | Cache semantics, copy safety, checklist equivalence, no-overdraw under 25 concurrent spends, atomic counters, single advance under 12 simultaneous loads. |

**Dependencies:** none added or removed. **Behavior changes visible to users:** the leaderboard can
lag by up to 30 s within a round. During the second or so while another session is advancing the
round, a page may render the old round until the next click.

**Compatibility:** `st.cache_data`/`st.cache_resource` require Streamlit ≥ 1.18, and
`requirements.txt` already requires ≥ 1.32. WAL needs a normal local filesystem, which Community
Cloud has. The code falls back silently if WAL is unavailable.

## D. Testing results

| Item | Status |
|---|---|
| Syntax check of every changed file (AST parse) | ✅ Passed |
| `tests/test_perf_safety.py` | ⚠️ Written, **not run** (execution was blocked in the review environment) |
| Max concurrency tested | Not measured |
| Responsiveness / p95 / CPU / peak memory | Not measured |
| SQLite micro-benchmark (independent of the app) | Measured: 0.34 ms per connect-per-query vs 0.23 ms reused; WAL cut lock errors 50 → 15 |

## E. Recommended next steps, not implemented (need your decision)

1. **[Critical, data] Move persistence off the container.** Use a free hosted database, such as
   Turso/libSQL (SQLite-compatible, smallest code change), Supabase Postgres, or Neon. At minimum, add
   a Director "Download backup / Restore backup" of `venture_foundry.db` and take a backup each class
   day.
2. **[High, security] The landing page lists every team for anyone.** The *"Instructor demo: pick a
   team directly"* expander lets any visitor enter any team without a join code. The landing page
   also prints the default PIN (`foundry`). Recommendation: show the demo picker only after Director
   login, and stop displaying the default PIN.
3. **[High] Slow AI mail on advance.** When Managing-Partner notes are on, the session that triggers
   an advance makes one AI request per team, serially, with up to a 25 s timeout each. The new lock
   keeps other students from waiting on it, but that one session can hang for minutes. Recommendation:
   send the notes in a background thread or on the Director's click.
4. **[Medium] Pin dependency versions** (for example `streamlit==1.x.*`) so a Cloud rebuild can't
   silently pick up a breaking release mid-semester.
5. **[Low]** Remove the stale `venture_foundry.zip` (an old copy of the app) from the repo.
6. **[Medium] Remaining lost-update patterns.** These are lower stakes than credits and money:
   skill-XP and training updates still read-modify-write. Convert them to atomic SQL if teammates
   report lost training progress.

## F. Remaining platform constraints

- **Code-level, now addressed:** N+1 reads, per-rerun init, uncached shared views, SQLite locking,
  advance and spend races.
- **Configuration:** upload cap. No supported Cloud setting adds CPU or memory.
- **Platform, not fixable in code:**
  - Community Cloud documents shared limits of roughly 0.078–2 CPU cores and 690 MB–2.7 GB RAM, which
    can change without notice.
  - All sessions share one Python process, so the GIL serializes the CPU work.
  - There's no horizontal scaling.
  - Apps sleep after inactivity, and waking takes time.
  - **Local files, including the database, are not preserved across reboot or redeploy.**
  - Actual CPU and memory for this app can't be observed from the dashboard, so they remain
    **unknown**.

**Is 30–40 concurrent users realistic?** For this workload (forms and text, no large files or
models), it is plausible *after* these changes. That's because the remaining per-click work is small
and memory per session is light. It is **not demonstrated.** Run the load test below before relying
on it. Don't claim 40-user support until it passes.

## 6. Load-test plan (run locally, not against production)

1. Seed a copy of the database with one game at round 8 or later (10 teams, some evidence,
   assumptions, and canvases). Point `VF_DB_PATH` at the copy.
2. Use Playwright with N headless browsers (N = 1, 5, 10, 20, 30, 40). Each joins a team by code,
   clicks through 5 pages, saves one form, and repeats for 5 minutes. Streamlit runs over WebSockets,
   so plain HTTP load tools won't produce realistic results.
3. Record per-click time to "script finished" (the stale-element overlay disappears), p50 and p95,
   errors, and `psrecord <pid>` CPU and RSS.
4. Run the same scenario on `main` and on this branch. Then include one forced scheduled advance
   during the 40-user run and confirm salaries are charged exactly once.
