# Venture Foundry — The Evidence Economy

A semester-long entrepreneurship simulation as a multi-team Streamlit app with
SQLite persistence. Student teams create, test, revise, finance, and defend a
new venture. The core rule: **teams don't earn points for a good idea — they
earn resources by producing credible evidence that their business model could work.**

## Run it

```bash
cd venture_foundry
pip install -r requirements.txt
streamlit run app.py
```

The app opens in your browser. A local `venture_foundry.db` file is created on
first run and holds all cohort state (survives restarts).

## Two roles

**🎩 Venture Foundry Director (instructor)** — log in with the PIN (default
`foundry`, change it under *Round Control*):

- **Team Setup** — two ways to create teams:
  - **⚡ Quick balanced setup** — enter a number of teams and pick a **difficulty level (Novice → Easy → Standard → Hard → Expert)**. Every team is created with *identical* starting capital, Evidence Credits, founder-hours, and market potential, so all teams have an equal opportunity for success. Choose whether territories are **distinct per team** (teams avoid competing for identical customers) or **the same for all** (maximum comparability), and whether founders are a **shared balanced card** or **varied archetypes** (resources are equalized either way). Join codes are listed for handout.
  - **Manual add** — create one team at a time with fully custom territory, founder card, and resources.
- **Schedule & Timing** — define **how many rounds** the simulation runs (default 15) and pack the curriculum into them however your class meets. Each round can cover **one OR more pieces of material**, so all 15 topics fit even in, say, 7 rounds. Clicking **Apply & auto-balance** splits the curriculum, in logical order, into **even-load rounds so no round is heavier than another** (each round shows its "load" = concepts + objectives). A **suggested balanced arrangement** is always previewed with per-round load; apply it in one click, then **move any concept** to a different round by hand. You can also **add/remove** material and set a **date/time** for each round to begin (auto-advances on next app load). One-click reset to the default 15-round order.
- **Round Control** — set the current round manually; see this round's objectives/concepts/task and the full schedule map.
- **Resources** — grant or deduct capital, credits, and hours (funding rounds, penalties).
- **Market Events** — issue events by category (Customer, Competitive, Operational, Regulatory & Ethical, Financial). Each event names the assumption it exposes. Broadcast to all teams, target one team, or roll a random event.
- **VP Auction** — inspect each team's value propositions and token allocations; override a proposition's evidence support to match the real evidence quality (which drives the automated tax/dividend).
- **Pivot Committee** — review pivot petitions and approve / approve conditionally / request more evidence / reject / classify as random change. Optionally charge the change cost.
- **Dashboard Scoring** — score the ten performance dimensions 0–100 per round.
- **Cohort Overview** — leaderboard across teams plus inspection of each team's canvases, assumptions, experiments, and reflections.
- **🤖 Auto-Director** — automates the Director's per-round decisions from each team's actual submitted work, with full override:
  - **Round-aligned** — recommendations only cover what's actually available that round: a dimension is scored only once the tool it depends on has been introduced, events aren't suggested until Market Events is introduced, and pivot recommendations wait until pivots are unlocked. (These follow the schedule, so they recompute if you reorder topics.)
  - **Predicted dashboard scores** (0–100) derived from canvases, evidence ledger, experiments, assumptions, the VP auction, and AI logs — every dimension has a transparent heuristic, and only in-play dimensions are shown/scored.
  - **Suggested market event** aimed at each team's biggest untested high-risk assumption (risk type → event category), with a stated reason.
  - **Recommended pivot decision** for each pending petition (Approved / Conditional / NeedsEvidence / Rejected) based on the evidence and completeness of the petition.
  - **Predicted valuation** shown per team before anything is applied.
  - **Tunable scoring weights** — a per-dimension weight slider (0–2×, default 1.0) lets you dial how strongly each dimension responds, or set one to 0 to ignore it — no code editing required.
  - **Per-round feedback emails** — auto-generates a personalized "venture review" for each team (strengths, where to focus, evidence quality, untested risks, a recommended next step, predicted valuation) delivered to the team's in-app **Inbox**. Preview/edit before sending, send per team, send to all, or auto-send on run.
  - Override any score, swap the event, or change a pivot call, then **Apply per team** or **Apply all suggestions**. Toggle each automation type on/off, and optionally **Run automatically on round advance** (manual or scheduled).

**🎓 Team (student)** — enter with the join code:

- **Round Briefing** — the starting point each round: learning objectives, concepts, tasks, and a **shaded completion checklist** ("To finish Round N — x/y complete") where amber items must still be done and green items are done. It also spells out **what must change this round** vs. **what can remain** (carried forward), and what's locked. Includes the full round-by-round arc.
- **Inbox** — an in-app "email" inbox that receives a per-round **venture review** from the Director/Auto-Director (strengths, focus areas, risks, next steps). Unread messages show a 🔵 badge in the sidebar.
- **Dashboard** — resources, live venture valuation, performance dimensions, and a warning list of high-importance untested assumptions.
- **Founder & Opportunity** — your founder card and territory; log ≥3 candidate ventures scored on importance, fit, access, evidence availability, affordability.
- **Canvases** — the real Strategyzer canvases in their canonical layouts: **Customer Profile** (the circle — gains / jobs / pains), the **Value Proposition Canvas** (value-map square beside the customer-profile circle, so the "fit" is visible), and the **Business Model Canvas** (the nine blocks in their standard grid positions). All versioned with dated change notes and full history. The three canvases are **staged across several rounds** (Customer Profile → VPC → BMC) so no single round is overloaded; the page shows the current round's focus canvas and flags any introduced later.
- **VP Auction** — field ≥3 competing value propositions, then privately allocate 100 Venture Tokens. The round scores automatically: an **Overconfidence Tax** hits tokens parked on weakly-supported propositions, and a **Learning Dividend** rewards redirecting tokens toward better-supported ones vs. your last auction. Net Evidence Credits are applied on submit; a live preview shows the outcome before you commit.
- **Assumption Map** — convert the venture into testable assumptions, classify by risk type (desirability / feasibility / viability / adaptability), importance, existing evidence, testability; auto-computed priority.
- **Experiment Marketplace** — buy experiment cards with limited money / hours / credits; you must state hypothesis, metric, success + failure thresholds, and decision rule *before* recording results.
- **Evidence Ledger** — log evidence against the strength ladder; behavioral evidence outranks opinion and earns Evidence Credits proportional to strength.
- **Market Events** — events pushed by the Director, each exposing an assumption.
- **Pivot Petition** — submit a formal, evidence-backed petition for committee review.
- **AI Assist Log** — where teams record every use of generative AI and verify it (see below).
- **Decision Journal** — individual weekly reflections for accountability.

## Curriculum, progressive complexity & scheduling

The simulation adds complexity one round at a time. Each round has defined
**learning objectives** and **concepts** (taught in the first class session), with
the second session being the simulation round that applies them. `content.py` holds
the ordered `CURRICULUM_TOPICS`; the **schedule** (a SQLite table) maps each round
to a topic and an optional advance time, and tool unlocks are derived from wherever
each topic sits in that schedule — so everything follows your reordering automatically.

- **Configurable length** — the Director sets the number of rounds (default 15) on **Schedule & Timing**.
- **Cover all material in fewer rounds, balanced** — a round can hold several topics, so the full 15-topic curriculum fits into however many rounds the class meets (e.g. all 15 in 7). The app **auto-balances by logical content** — a contiguous, even-load split so no round is heavier than another — and shows a suggested arrangement you can apply or override.
- **Add / remove / move material** — freely reassign topics between rounds by hand; unlocks and canvas staging recompute to match. Unplaced topics wait in an Unassigned pool.
- **Timed advancement** — set a date/time per round; the sim auto-advances to that round the next time the app is loaded after the time passes (no background server required).
- **Round-gated tools (Strict round mode, default on)** — students can only *edit* tools relevant to the current round. Not-yet-introduced tools are **🔒 locked** (view-only lock screen); previously-used tools that aren't part of this round are **👁️ reference-only** (visible, edits disabled) so work carries forward without being changed; the round's active tools are editable and show a shaded "Required on this page this round" checklist. The Director can turn Strict round mode off on **Round Control** to let teams edit any unlocked tool anytime.
- The default arc runs founder/opportunity formation → customer discovery → value proposition → business model → assumptions → experiments → market testing → pivots → economics → scaling → investment defense.

## Generative AI + the AUDIT verification methodology

Students are expected to use generative AI every round — but the app enforces the
course's core principle that **AI output is confident opinion, not evidence**. Any
AI suggestion is treated as evidence strength 0 until it passes the **AUDIT** check
and is translated into real-world evidence:

- **A — Assumptions surfaced**: what must be true for the AI's suggestion to hold?
- **U — Unsupported claims flagged**: which parts are confident but unproven?
- **D — Data & sources checked**: hallucinations, stale data, bias?
- **I — Independent test designed**: the cheapest real test to verify it.
- **T — Translate to evidence**: the strength the real test produced.

Teams log each AI use on the **AI Assist Log** page and complete the AUDIT; entries
stay *Unverified* until a real test supports them. A one-click AUDIT reminder also
appears on the Canvases, Assumptions, VP Auction, and Pivot pages, and the Director
reviews every team's AI use (and how much remains unverified) from the **AI use** tab
on Cohort Overview.

## The models built in

- **Evidence-strength ladder** (0–10): founder opinion → … → binding payment. Editable in `content.py`.
- **Evidence Credits**: logging evidence pays credits = strength × `CREDITS_PER_STRENGTH`.
- **Venture valuation**: `Market Potential × Evidence Confidence × BM Coherence × Execution Factor − Unresolved Risk`. Each index maps a 0–100 dashboard score onto 0.50–1.50.
- **Recognition dimensions**: strongest evidence-based venture, most improved model, best customer insight, most disciplined experiment portfolio, best responsible pivot, highest investor confidence, best overall — so an attractive starting idea can't dominate.
- **VP Auction scoring**: `alignment = Σ(tokens × evidence_support) / Σtokens`; `Overconfidence Tax = (1 − alignment) × OVERCONFIDENCE_TAX_MAX`; `Learning Dividend = max(0, alignment − prev_alignment) × LEARNING_DIVIDEND_MAX`. All three constants are editable in `content.py`.

## Keeping teams on equal footing

The whole point of Quick Setup is a fair start. Recommended practices, several
enforced by the app:

- **One difficulty for the cohort** — Quick Setup applies the same resource preset to every team; the current level shows in the Director sidebar and on Cohort Overview.
- **Equalized resources** — even the "varied founder archetypes" option overrides each card's money and hours so no team is richer at kickoff.
- **Distinct territories** to stop teams scooping identical customers, or the same territory for a pure head-to-head — your call, odds are equal either way.
- **Broadcast market events** so every team faces the same shock in the same round (use the "All teams" target or the 🎲 random-broadcast button).
- **Balance check** — Cohort Overview flags whether every team still has identical starting resources, so you can spot an accidentally mis-created team.

## Tuning the game

All content — territories, founder cards, experiment cards, market events,
evidence ladder, dashboard dimensions, semester map, and the **difficulty presets**
(`DIFFICULTY_LEVELS`) — lives in `content.py`. Edit it without touching the app logic.

## File map

| File | Purpose |
|------|---------|
| `app.py` | Routing, login, role shells |
| `db.py` | SQLite schema + all data access |
| `content.py` | Game content (cards, ladders, tables, difficulty presets) |
| `logic.py` | Valuation, evidence economy, quick-setup, analytics |
| `branding.py` | Simulation logo (inline SVG) + header/sidebar helpers |
| `assets/logo.svg` | The logo as a standalone SVG file (README, favicons, print) |
| `views_student.py` | Team screens |
| `views_instructor.py` | Director console |

## Notes

- Default instructor PIN is `foundry`; change it immediately under *Round Control*.
- The app is designed as the "enhanced application version" from the design doc. AI role-players (customer / investor / partner / regulator agents) are not included — they can be layered on later via a connector.
- Move `venture_foundry.db` to back up or reset a cohort. Set `VF_DB_PATH` to relocate it.
