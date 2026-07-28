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

- **Team Setup** — create teams, assign an opportunity territory + founder card, set starting capital / Evidence Credits / founder-hours / market potential. Each team gets a unique join code.
- **Round Control** — advance the 15-week semester; view the week-by-week map.
- **Resources** — grant or deduct capital, credits, and hours (funding rounds, penalties).
- **Market Events** — issue events by category (Customer, Competitive, Operational, Regulatory & Ethical, Financial). Each event names the assumption it exposes. Broadcast to all teams, target one team, or roll a random event.
- **VP Auction** — inspect each team's value propositions and token allocations; override a proposition's evidence support to match the real evidence quality (which drives the automated tax/dividend).
- **Pivot Committee** — review pivot petitions and approve / approve conditionally / request more evidence / reject / classify as random change. Optionally charge the change cost.
- **Dashboard Scoring** — score the ten performance dimensions 0–100 per round.
- **Cohort Overview** — leaderboard across teams plus inspection of each team's canvases, assumptions, experiments, and reflections.

**🎓 Team (student)** — enter with the join code:

- **Dashboard** — resources, live venture valuation, performance dimensions, and a warning list of high-importance untested assumptions.
- **Founder & Opportunity** — your founder card and territory; log ≥3 candidate ventures scored on importance, fit, access, evidence availability, affordability.
- **Canvases** — versioned Customer Profile, Value Proposition Canvas, and Business Model Canvas with dated change notes and full history.
- **VP Auction** — field ≥3 competing value propositions, then privately allocate 100 Venture Tokens. The round scores automatically: an **Overconfidence Tax** hits tokens parked on weakly-supported propositions, and a **Learning Dividend** rewards redirecting tokens toward better-supported ones vs. your last auction. Net Evidence Credits are applied on submit; a live preview shows the outcome before you commit.
- **Assumption Map** — convert the venture into testable assumptions, classify by risk type (desirability / feasibility / viability / adaptability), importance, existing evidence, testability; auto-computed priority.
- **Experiment Marketplace** — buy experiment cards with limited money / hours / credits; you must state hypothesis, metric, success + failure thresholds, and decision rule *before* recording results.
- **Evidence Ledger** — log evidence against the strength ladder; behavioral evidence outranks opinion and earns Evidence Credits proportional to strength.
- **Market Events** — events pushed by the Director, each exposing an assumption.
- **Pivot Petition** — submit a formal, evidence-backed petition for committee review.
- **Decision Journal** — individual weekly reflections for accountability.

## The models built in

- **Evidence-strength ladder** (0–10): founder opinion → … → binding payment. Editable in `content.py`.
- **Evidence Credits**: logging evidence pays credits = strength × `CREDITS_PER_STRENGTH`.
- **Venture valuation**: `Market Potential × Evidence Confidence × BM Coherence × Execution Factor − Unresolved Risk`. Each index maps a 0–100 dashboard score onto 0.50–1.50.
- **Recognition dimensions**: strongest evidence-based venture, most improved model, best customer insight, most disciplined experiment portfolio, best responsible pivot, highest investor confidence, best overall — so an attractive starting idea can't dominate.
- **VP Auction scoring**: `alignment = Σ(tokens × evidence_support) / Σtokens`; `Overconfidence Tax = (1 − alignment) × OVERCONFIDENCE_TAX_MAX`; `Learning Dividend = max(0, alignment − prev_alignment) × LEARNING_DIVIDEND_MAX`. All three constants are editable in `content.py`.

## Tuning the game

All content — territories, founder cards, experiment cards, market events,
evidence ladder, dashboard dimensions, semester map — lives in `content.py`.
Edit it without touching the app logic.

## File map

| File | Purpose |
|------|---------|
| `app.py` | Routing, login, role shells |
| `db.py` | SQLite schema + all data access |
| `content.py` | Game content (cards, ladders, tables) |
| `logic.py` | Valuation, evidence economy, analytics |
| `views_student.py` | Team screens |
| `views_instructor.py` | Director console |

## Notes

- Default instructor PIN is `foundry`; change it immediately under *Round Control*.
- The app is designed as the "enhanced application version" from the design doc. AI role-players (customer / investor / partner / regulator agents) are not included — they can be layered on later via a connector.
- Move `venture_foundry.db` to back up or reset a cohort. Set `VF_DB_PATH` to relocate it.
