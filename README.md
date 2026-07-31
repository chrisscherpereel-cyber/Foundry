# Venture Foundry — From hunch to hard evidence

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
  - **Welcome email preview/edit** — expand any team to **preview and edit its Round-1 welcome email** before students see it (subject + body, with a live markdown preview), then send the edited version or resend the auto-written one. Each team shows whether its welcome has been sent.
- **Schedule & Timing** — define **how many rounds** the simulation runs (default 15) and pack the curriculum into them however your class meets. Each round can cover **one OR more pieces of material**, so all 15 topics fit even in, say, 7 rounds. Clicking **Apply & auto-balance** splits the curriculum, in logical order, into **even-load rounds so no round is heavier than another** (each round shows its "load" = concepts + objectives). A **suggested balanced arrangement** is always previewed with per-round load; apply it in one click, then **move any concept** to a different round by hand. You can also **add/remove** material and set a **date/time** for each round to begin (auto-advances on next app load). One-click reset to the default 15-round order.
- **Round Control** — **the page you advance the simulation from.** A prominent **▶️ Advance to Round N+1** button moves the whole cohort forward one round, which is what **unlocks the next round's tools for every team** (it also applies learning, resets founder hours, and charges specialist salaries); the button previews exactly which material and tools the next round unlocks. An expander offers **go back a round** and **jump to a specific round** for non-sequential moves. The two ways to advance are spelled out: click Advance here, or set date/times on Schedule & Timing to advance automatically (the page shows any scheduled auto-advance). Also toggle Strict round mode; and tune the **Economy & balance** (founder-hours per round for all teams, training cost per level, and part-/full-time hire boost, upfront, and salary) without editing code. Also shows this round's objectives/concepts/task and the schedule map. **Under Strict round mode a tool or canvas that isn't part of the current round is fully view-only: its input widgets and "add" forms don't render at all** (not just its Save button), so teams can't enter work early. The view-only notice **names the exact round(s) the tool/canvas opens** (e.g. "the Value Proposition Canvas is the focus in Rounds 5 and 6"). Existing work still shows read-only and carries forward. Turn Strict mode off to let teams edit anything at any time.
- **Resources** — grant or deduct capital, credits, and hours (funding rounds, penalties).
- **Market Events** — issue events by category (Customer, Competitive, Operational, Regulatory & Ethical, Financial). Each event names the assumption it exposes. Broadcast to all teams, target one team, or roll a random event.
- **VP Auction** — inspect each team's value propositions and token allocations; override a proposition's evidence support to match the real evidence quality (which drives the automated tax/dividend).
- **Pivot Committee** — review pivot petitions and approve / approve conditionally / request more evidence / reject / classify as random change. Optionally charge the change cost.
- **Dashboard Scoring** — score the ten performance dimensions 0–100 per round.
- **Round Scores** — one automated **0–100 grade per team** for the work they committed in a round. It blends up to five components — **commitment/completion** (share of the round's decisions + concept-checks done), **evidence quality**, **business-model coherence**, **concept coverage**, and **AI verification** (share of AI uses actually evaluated; `n/a` if the team hasn't used AI) — then subtracts a **risk penalty** for important, still-untested assumptions. **Only what a team could actually do that round is counted:** evidence and coherence are skipped (shown as `n/a`) until their tools are introduced, the risk penalty waits until the Assumption Map exists, and the weights **renormalize over whatever counts** — so a team is never marked down for a tool it doesn't have yet. **Concept answers that reference the team's own territory and the venture they're building score fully; generic answers score partially**, so the grade rewards work grounded in their actual business. A **sensitivity panel** lets you set each component's **weight** (normalized) and a **strictness dial** (lenient ↔ harsh) with one-click reset. The table ranks all teams live, marks which components were counted, and shows whether each committed; you can **preview/edit and email** any team its score breakdown, or send to all.
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
  - **Course corrections (mini-pivots) from round 1** — a lightweight "Changed your mind?" panel lets a team log a quick, self-approved course-correction (what they believed, the evidence that changed it, what they'll change) **from the very first round** — normalizing productive failure early, when the cost of being wrong is low. Each one earns a small Evidence-Credit learning reward and counts toward their course-correction trend. The heavyweight **Pivot Petition** (investment-committee review) still unlocks later for major changes.
  - **Sidebar progress tracker** — the team sidebar shows a live **"Round N to-do: x/y done"** bar with an expander listing exactly what's still open and on which tool (including anything carried over), so from any page the team can see what's left this round.
  - **Decision deadline & commit (with a full lock)** — the team **commits and withdraws right from the sidebar**, so the control is one click away from every page. The sidebar shows a live ✅ committed / ⚠️ not-committed banner (with time remaining) and the matching button: **✅ Commit round** or **↩️ Withdraw to edit**. **Committing freezes the whole team side** — every tool becomes view-only (its inputs and forms stop rendering), so a team can't quietly change committed work and forget to re-commit. To edit again they **Withdraw** (allowed any time before the deadline), which re-opens all tools; they then **Commit** again when done. Every tool page shows a clear "this round is committed — withdraw in the sidebar to edit" banner while locked. The deadline itself comes from the schedule's next-round advance time; if none is set the sidebar and Round Briefing **say so explicitly**. Once the deadline passes the round **locks for good** and the last committed work is what's scored. The Round Briefing still lists exactly which decisions are open before you commit.
- **Inbox** — an in-app "email" inbox. On creation, every team receives a **Round-1 welcome email** that welcomes the founders, maps out their **opportunity territory** (who the customers are, where to find them, how to start), reads their **founder card** for strengths to lean on and gaps to train or hire around, and gives **subtle Round-1 hints**. Each round after that, the Inbox receives a per-round **venture review** from the Director/Auto-Director (strengths, focus areas, risks, next steps) that now ends with **subtle "to do well in this round" hints** for the round's topics. Unread messages show a 🔵 badge in the sidebar.
- **Concept Check** — guarantees every concept introduced that round is covered, but **only asks a written question when it has to**. Most concepts are covered automatically by the **decisions the team makes in the tools** (e.g. building the Customer Profile covers "customer jobs, pains, gains"); the page lists those as ✅ covered-by-decision with no writing. Only concepts that need judgment and have no hands-on task (e.g. "behavior vs. opinion", "sunk-cost discipline") get a short written answer. If a round's concepts are all decision-covered, there's nothing to write. (This page sits just before the AI Assist Log in the sidebar.)
- **Founder & Team** — a realistic model of the founding team:
  - **Founder effort = the time you assign to tasks.** Teams don't set effort directly; it's the **dynamic sum** of admin + managing hires + business‑development budget + training + hiring, shown with a **color‑coded bar (green ≤40h, yellow ≤60h, red ≤80h)** and **hard‑capped at 80 hours**. **Admin grows as the venture (round) gets more complex**, and managing hires costs founder time. The team assigns the rest: a **business‑development budget** (hours for experiments) and **training hours per skill**. **Training banks the exact hours you assign** — the default is a full level, but partial hours carry over to a later round (early levels are cheaper, higher levels cost more). A **Pareto chart** shows where the week goes and always sums to current effort. Everything **resets each round** (unused business‑dev hours are lost). (Setting the allocation is a Round‑1 deliverable; "founder & team time allocation" is a Round‑1 concept.)
  - **Skills** — seven capabilities (Customer Research, Design & Prototyping, Technical/Engineering, Sales & Growth, Finance & Unit Economics, Operations, Responsible Innovation), each with a defined meaning and a real effect (raises its matching performance dimension). Founders improve them three ways: **training** (invest founder-hours, which **bank as progress** — 8 of 10 hours carries over and finishes next round; **undoable** for a refund), **hiring**, and **learning by doing** — finishing a round's own work banks progress on the skills that round leaned on.
  - **Hiring** — founders can't do everything. When a needed skill is weak, **hire a specialist part-time or full-time**. Hiring costs **money + recruiting time** upfront and an ongoing **salary + management time** each round (managing people is real founder time that can't go to building or training). A hire raises your **effective** skill (founder level + hires, capped at 5). Let a hire go to stop the cost. The page flags which skills the **current round** leans on so you know when to train vs. hire.
- The founder card itself is shown as a styled persona card on **Founder & Opportunity**, with a ❓ on each attribute explaining what it means.
- **Dashboard** — resources, live venture valuation (a brand-new idea is worth **$0**; value is *earned* as the team builds its model, tests assumptions, and logs strong evidence — shown as *potential* value × an **evidence-coverage %**), performance dimensions, and a warning list of high-importance untested assumptions.
- **Progress** — the team's **own learning trend**, made visible so they can self-regulate instead of gaming a score: behavioral-vs-opinion evidence counts and ratio, average evidence strength, **assumption test-coverage %**, **evidence-coverage %**, **evidence-driven course corrections**, and **AI-verification %** — each shown as a live snapshot and as a **line chart over the rounds** (a per-round metrics history is captured automatically as rounds advance).
- **Founder & Opportunity** — your founder card and territory; log ≥3 candidate ventures scored on importance, fit, access, evidence availability, affordability.
- **Canvases** — four canvases in layouts that mirror the printed originals (each with a schematic header): **Customer Profile** (the circle — Gains top-left, Customer Jobs right, Pains bottom-left), the **Value Proposition Canvas** (value-map square beside the customer-profile circle), the **Business Model Canvas** (the nine blocks in their standard grid), and the **Business Model Environment Canvas** (the UNITE trends-and-forces scan: customer/technology/mega trends across the top, market/industry/macro forces across the bottom, disruptive competitive forces at the centre). All versioned with dated notes and history. Each canvas is **staged to its own round** (Customer Profile → VPC → BMC → Environment); under **Strict round mode** a canvas is *editable only in the round it belongs to* (others are view-only), and any unfinished earlier canvas is re-activated until completed.
- **VP Auction** — field ≥3 competing value propositions, then privately allocate 100 Venture Tokens. The round scores automatically: an **Overconfidence Tax** hits tokens parked on weakly-supported propositions, and a **Learning Dividend** rewards redirecting tokens toward better-supported ones vs. your last auction. Net Evidence Credits are applied on submit; a live preview shows the outcome before you commit.
- **Assumption Map** — convert the venture into testable assumptions, classify by risk type (desirability / feasibility / viability / adaptability), importance, existing evidence, testability; auto-computed priority.
- **Experiment Marketplace** — buy experiment cards with limited money / hours / credits; you must state hypothesis, metric, success + failure thresholds, and decision rule *before* recording results.
  - **Predict-before-you-run (calibration loop)** — when designing an experiment the team also commits a **prediction** (will this Support/Refute/Inconclusive the assumption?) and a **confidence %**. After recording the result, each experiment shows **prediction vs. actual** (right ✅ or wrong ❌ — "that gap is the lesson"), and a **calibration scoreboard** tracks hit-rate, average confidence, and the **calibration gap** (confidence − hit-rate). A positive gap warns the team it's been *more confident than correct* — the classic founder trap — and nudges it to cheaply test its strongest hunches first.
- **Evidence Ledger** — log evidence against the strength ladder; behavioral evidence outranks opinion and earns Evidence Credits proportional to strength.
  - **Justify the strength + misclassification flags** — logging now requires a one-line **"why is this that strength?"** justification (behavior vs. opinion), and a live **misclassification check** compares the team's wording to the strength they chose. If a stated intention ("they said they'd buy") is logged as strong behavioral evidence — or a real action is under-rated as an opinion — the team gets a gentle 🔎 nudge *before* logging, and flagged items are marked in their ledger. A **⚠️ Flagged** count surfaces on the Evidence page and in the Director's **Cohort Overview** as a coaching signal (not an automatic penalty). This makes telling behavior from opinion — the simulation's central skill — something students practice, not just declare.
- **Market Events** — events pushed by the Director, each exposing an assumption.
- **Pivot Petition** — submit a formal, evidence-backed petition for committee review.
- **AI Assist Log** — turns AI *use* into AI *evaluation*, and makes it fast enough to take seriously. Logging is a **two-field quick-log** (the AI's **claim** + **how you'll check it**), with one-tap structured picks (claim type, whether a source was given) and an optional deeper AUDIT. You can **log AI in-context** — the "Used AI here?" panel on the Canvases, Assumptions, and Experiment pages logs it right there with the round and area pre-filled. **Link a claim to an assumption and it auto-verifies**: when that assumption tests Supported/Refuted, the log flips to Verified/Rejected with no extra step. Status is set with **one-click buttons** (✅ Verified / ❌ Rejected / ✏️ Modified / ⏳ Unverified), and an **"N unverified" nudge** plus a verification-rate bar keep it honest. The round score's **AI-verification** component rewards the share you actually evaluated — **not** usage — and is neutral (`n/a`) for teams that don't use AI.
- **Decision Journal** — a fast, **round-adaptive** individual reflection. Three core prompts every round plus **one focus prompt that changes with the round's topic** (e.g. customer-discovery weeks ask "what surprised you talking to real customers?"; pricing weeks ask about willingness-to-pay). It **pre-fills your name** (remembered for the session) and the round, shows a **this-round summary** of your own metrics as a memory jog, and surfaces **last round's "what we'd do differently"** so you can close the loop. The core prompts are **round-aware** — Round 1 asks forward-looking, answerable questions (you can't assess "how you did" before the round happens); later rounds ask the retrospective versions. Only the three core prompts are required (the rest are optional, with starter stems), you can **come back and edit** your entry (no duplicates), and the team sees who's journaled this round. A commit-time nudge reminds anyone who hasn't written one.

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
- **Total coverage + carry-forward** — a round is complete only when every **decision** deliverable is done AND every **concept** is covered (a matching decision or a Concept Check answer). Any unfinished deliverable or unanswered concept from an earlier round is **carried into the current round's checklist**, and its tool is re-activated (editable) so the team can finish it — nothing is silently skipped.
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
- **Venture valuation** (evidence-weighted): `Potential = Market Potential × Evidence Confidence × BM Coherence × Execution Factor` (each index maps a 0–100 dashboard score onto 0.50–1.50); then `Valuation = Potential × Evidence Coverage − Unresolved Risk`. **Evidence coverage** (0–1) discounts the opportunity by how much of the model the team has actually proven — it blends the share of *important* assumptions they've tested (50%), the strength of their evidence portfolio (35%), and model-building work such as drafting canvases and naming assumptions (15%), with a **floor of 0**. So a brand-new venture with no work is worth **exactly $0**, and value is **earned**: it rises as the team builds its model and climbs toward full potential as assumptions are tested and strong (behavioral) evidence is logged. The Dashboard shows both the potential figure and the current coverage %, and the Director's Cohort Overview shows an **Evidence-backed %** column. Tunable via `COVERAGE_FLOOR`, `COVERAGE_STRENGTH_TARGET`, and `COVERAGE_IMPORTANCE_MIN` in `logic.py`.
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
