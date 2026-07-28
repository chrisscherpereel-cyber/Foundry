"""
views_instructor.py — Venture Foundry Director (instructor) console.

Like the student views, every screen has a "How this page works" panel and every
input carries a hover-help (ⓘ) tooltip so a first-time instructor can run the
whole simulation without a separate manual.
"""

import random

import streamlit as st

import db
import content
import logic


def _guide(what, steps=None, terms=None, expanded=True):
    """Plain-language 'How this page works' panel (see student views for details)."""
    with st.expander("ℹ️ How this page works", expanded=expanded):
        st.markdown(what)
        if steps:
            st.markdown("**What to do here**")
            st.markdown("\n".join(f"{i+1}. {s}" for i, s in enumerate(steps)))
        if terms:
            st.markdown("**Key terms**")
            st.markdown("\n".join(f"- **{t}** — {d}" for t, d in terms))


# --------------------------------------------------------------------------- #
# Round control & semester map
# --------------------------------------------------------------------------- #
def round_control():
    st.subheader("🎛️ Round & Semester Control")
    _guide(
        "You are the Venture Foundry Director. This page sets which week (round) the whole "
        "cohort is on and lets you change the login PIN. The current round is stamped onto "
        "events, scores, and reflections, and it drives the semester map below so you always "
        "know what students should be working on.",
        steps=[
            "Set the current round to match your class week, then click Set round.",
            "Change the instructor PIN from the default and click Update PIN.",
            "Use the 15-week map as your run-of-show for what happens each week.",
        ],
        terms=[
            ("Round", "The current simulation week (1–15). Everything new is tagged with it."),
            ("Instructor PIN", "The password teams cannot see; it opens this Director console."),
        ],
    )
    cur = db.current_round()
    c1, c2 = st.columns([1, 3])
    with c1:
        new_round = st.number_input(
            "Current round", 1, 15, cur,
            help="The class week the whole cohort is on. Tagged onto new events, scores, and "
                 "reflections.")
        if st.button("Set round", help="Apply the round number to the whole cohort."):
            db.set_setting("current_round", int(new_round))
            st.success(f"Round set to {new_round}.")
            st.rerun()
    with c2:
        pin = st.text_input(
            "Instructor PIN (change)", value=db.get_setting("instructor_pin", "foundry"),
            help="The password for this Director console. Change it from the default 'foundry' "
                 "so students can't open it.")
        if st.button("Update PIN", help="Save the new instructor PIN."):
            db.set_setting("instructor_pin", pin)
            st.success("PIN updated.")

    st.divider()
    st.write("### 15-week semester map")
    st.caption("Your week-by-week run-of-show. The highlighted row is the current round.")
    row = next((s for s in content.SEMESTER if s[0] == cur), None)
    if row:
        st.info(f"**Week {row[0]} — {row[1]}**  ·  Strategyzer: {row[2]}  ·  "
                f"Evidence produced: {row[3]}")
    st.dataframe(
        [{"Week": w, "Venture stage": stage, "Strategyzer concepts": concept,
          "Evidence produced": ev} for w, stage, concept, ev in content.SEMESTER],
        use_container_width=True, hide_index=True,
    )


# --------------------------------------------------------------------------- #
# Team setup
# --------------------------------------------------------------------------- #
def team_setup():
    st.subheader("👥 Team Setup")
    _guide(
        "Create each student team here. A team gets an opportunity territory (a problem area, "
        "not a product), a founder card (their fixed skills and constraints), and starting "
        "resources. When you create a team the app generates a **join code** — give that code "
        "to the students so they can log in. You can also change a team's stage or risk penalty "
        "later in the list below.",
        steps=[
            "Type a team name.",
            "Pick an opportunity territory and a founder card (these fill in sensible defaults).",
            "Adjust starting capital, credits, hours, and market potential if you wish.",
            "Click Create team, then copy the join code to the students.",
            "Later, expand any team to change its stage or unresolved-risk penalty.",
        ],
        terms=[
            ("Opportunity territory", "The broad problem space the team explores."),
            ("Founder card", "The team's fixed skills, network, budget, and hours."),
            ("Join code", "The code students enter to access their team."),
            ("Market potential", "The dollar ceiling used in the valuation formula."),
            ("Unresolved-risk penalty", "A dollar amount subtracted from a team's valuation for "
             "risks they haven't retired."),
        ],
    )

    with st.form("create_team", clear_on_submit=True):
        name = st.text_input("Team name", help="A label for the team, e.g. 'Team Kestrel.'")
        c1, c2 = st.columns(2)
        opportunity = c1.selectbox(
            "Opportunity territory", content.OPPORTUNITY_TERRITORIES,
            help="The problem area this team will explore. They invent their own products "
                 "inside it.")
        card_name = c2.selectbox(
            "Founder card", [c["name"] for c in content.FOUNDER_CARDS],
            help="The team's fixed capabilities and constraints. Selecting one fills in the "
                 "default budget and hours below.")
        card = next(c for c in content.FOUNDER_CARDS if c["name"] == card_name)
        c3, c4, c5, c6 = st.columns(4)
        capital = c3.number_input(
            "Starting capital $", 0, 100000, int(card["budget"]),
            help="Simulated cash the team can spend on experiments and pivots.")
        credits = c4.number_input(
            "Evidence Credits", 0, 1000, 10,
            help="Starting Evidence Credits — the main currency. Teams earn more by logging "
                 "evidence.")
        hours = c5.number_input(
            "Founder-hours", 0, 1000, int(card["hours"]),
            help="The team's available time budget for the semester.")
        potential = c6.number_input(
            "Market potential $", 0, 100000000, 1000000, step=100000,
            help="The market-size ceiling used in the valuation formula.")
        if st.form_submit_button("Create team",
                                 help="Create the team and generate its join code.") and name:
            code = db.create_team(name, opportunity, card, capital, credits, hours, potential)
            st.success(f"Team '{name}' created. Join code: **{code}** — give this to the students.")
            st.rerun()

    st.divider()
    st.write("### Teams")
    st.caption("Expand a team to change its stage or risk penalty, or to delete it.")
    teams = db.list_teams()
    if not teams:
        st.info("No teams yet. Create your first team with the form above.")
        return
    for t in teams:
        with st.expander(f"{t['name']}  ·  code {t['join_code']}  ·  ${t['capital']:,.0f} · "
                         f"{t['evidence_credits']:.1f} credits"):
            st.write(f"Territory: {t['opportunity']}")
            st.write(f"Stage: {t['stage']}")
            new_stage = st.selectbox(
                "Venture stage", content.VENTURE_STAGES,
                index=content.VENTURE_STAGES.index(t["stage"]) if t["stage"] in content.VENTURE_STAGES else 0,
                key=f"stage_{t['id']}",
                help="The team's current phase. Advance it as they progress through the semester.")
            new_risk = st.number_input(
                "Unresolved-risk penalty $", 0, 10000000,
                int(t["unresolved_risk"]), step=25000, key=f"risk_{t['id']}",
                help="Dollars subtracted from this team's valuation for risks they haven't yet "
                     "addressed. Raise it when big assumptions stay untested.")
            c1, c2 = st.columns(2)
            if c1.button("Save", key=f"savet_{t['id']}",
                         help="Save the stage and risk penalty for this team."):
                db.update_team(t["id"], stage=new_stage, unresolved_risk=new_risk)
                st.success("Saved.")
                st.rerun()
            if c2.button("Delete team", key=f"delt_{t['id']}",
                         help="Permanently remove this team and all its data."):
                db.delete_team(t["id"])
                st.rerun()


# --------------------------------------------------------------------------- #
# Resources (grant / deduct)
# --------------------------------------------------------------------------- #
def resources():
    st.subheader("💰 Grant / Deduct Resources")
    _guide(
        "Hand out or take back resources here — an investor round adds capital, a funding "
        "request adds credits, a penalty removes them. Enter positive numbers to give and "
        "negative numbers to take. Every change is logged in the team's transaction ledger, "
        "and the reason you type appears there, so keep it descriptive.",
        steps=[
            "Pick the team.",
            "Enter the change for capital, credits, and/or hours (negative = deduct).",
            "Type a short reason (it's recorded in the ledger).",
            "Apply the adjustment.",
        ],
        terms=[
            ("Δ (delta)", "The change to apply. +500 adds 500; −500 removes 500."),
            ("Reason", "A note stored in the team's transaction history for transparency."),
        ],
    )
    teams = db.list_teams()
    if not teams:
        st.info("No teams yet. Create teams on the Team Setup page first.")
        return
    team = st.selectbox("Team", teams, format_func=lambda t: t["name"],
                        help="Which team to adjust.")
    c1, c2, c3 = st.columns(3)
    c1.metric("Capital", f"${team['capital']:,.0f}")
    c2.metric("Evidence Credits", f"{team['evidence_credits']:.1f}")
    c3.metric("Founder-hours", f"{team['founder_hours']:.0f}")

    with st.form("adjust_res", clear_on_submit=True):
        cc1, cc2, cc3 = st.columns(3)
        money = cc1.number_input(
            "Δ Capital $", -100000, 100000, 0, step=100,
            help="Positive adds cash (investor round); negative removes it (penalty).")
        credits = cc2.number_input(
            "Δ Evidence Credits", -1000, 1000, 0,
            help="Positive grants credits (funding request); negative removes them.")
        hours = cc3.number_input(
            "Δ Founder-hours", -1000, 1000, 0,
            help="Positive adds time; negative removes it.")
        desc = st.text_input(
            "Reason", placeholder="Investor round, funding request, penalty…",
            help="A short note recorded in the team's transaction ledger.")
        if st.form_submit_button("Apply adjustment",
                                 help="Apply the change and log it to the team's ledger."):
            ok, msg = db.adjust_resources(team["id"], money=money, credits=credits, hours=hours,
                                          kind="director", description=desc, allow_negative=True)
            st.success("Applied.") if ok else st.error(msg)
            st.rerun()


# --------------------------------------------------------------------------- #
# Market events
# --------------------------------------------------------------------------- #
def events():
    st.subheader("📡 Issue Market Events")
    _guide(
        "Market events are the twists you inject each round — a competitor move, a rule change, "
        "a cost shock. Every built-in event names the assumption it targets, so you can steer "
        "teams toward the risks they've been ignoring. Send an event to one team or broadcast "
        "to all. Start around week 7, one event per round. The dice button issues a random one "
        "if you're short on time.",
        steps=[
            "Pick a category, then a specific event (its exposed assumption is shown).",
            "Choose a target: one team, or 'All teams' to broadcast.",
            "Set the round, then click Issue event.",
            "Or click the 🎲 button to issue a random event to everyone.",
        ],
        terms=[
            ("Category", "The kind of shock: Customer, Competitive, Operational, Regulatory & "
             "Ethical, or Financial."),
            ("Exposed assumption", "The belief this event pressures — the teaching point."),
            ("Broadcast", "Send the same event to every team at once."),
        ],
    )
    teams = db.list_teams()

    with st.form("issue_event", clear_on_submit=True):
        category = st.selectbox(
            "Category", list(content.MARKET_EVENTS.keys()),
            help="The type of shock to introduce.")
        options = content.MARKET_EVENTS[category]
        idx = st.selectbox(
            "Event", range(len(options)), format_func=lambda i: options[i][0],
            help="The specific event. Each targets a common hidden assumption.")
        text, exposes = options[idx]
        st.caption(f"Exposes assumption: {exposes}")
        target = st.selectbox(
            "Target", ["All teams (broadcast)"] + [t["name"] for t in teams],
            help="Send to one team, or broadcast to the whole cohort.")
        rnd = st.number_input(
            "Round", 1, 15, db.current_round(),
            help="Which round this event belongs to. Defaults to the current round.")
        if st.form_submit_button("Issue event",
                                 help="Send this event to the chosen target."):
            if target == "All teams (broadcast)":
                db.add_event(None, int(rnd), category, text, exposes)
            else:
                tid = next(t["id"] for t in teams if t["name"] == target)
                db.add_event(tid, int(rnd), category, text, exposes)
            st.success("Event issued.")
            st.rerun()

    if st.button("🎲 Issue a random event to all teams",
                 help="Pick a random category and event and broadcast it to everyone this round."):
        cat = random.choice(list(content.MARKET_EVENTS.keys()))
        text, exposes = random.choice(content.MARKET_EVENTS[cat])
        db.add_event(None, db.current_round(), cat, text, exposes)
        st.success(f"Random {cat} event issued.")
        st.rerun()

    st.divider()
    st.write("### Event history")
    st.caption("Everything you've issued so far.")
    for e in db.list_events(None):
        scope = "All" if e["team_id"] is None else (db.get_team(e["team_id"]) or {}).get("name", "?")
        st.write(f"- R{e['round']} · **{e['category']}** · {scope} · {e['text']}")


# --------------------------------------------------------------------------- #
# Pivot committee
# --------------------------------------------------------------------------- #
def pivot_committee():
    st.subheader("⚖️ Pivot Committee")
    _guide(
        "Teams can't just declare a pivot — they file a petition and you rule on it. Your job "
        "is to check that the change is driven by evidence, not by frustration. Read each "
        "petition, then choose a decision. Approving (or approving conditionally) can "
        "automatically charge the team the change cost they proposed. Use 'Random Change' when "
        "a pivot looks unjustified — that's a teaching signal, not just a rejection.",
        steps=[
            "Expand a pending petition and read all fields.",
            "Choose a decision from the dropdown.",
            "Add a committee note explaining your reasoning (students see this).",
            "Leave 'Charge the change cost' ticked to deduct the cost on approval.",
            "Click Record decision.",
        ],
        terms=[
            ("Approved / Conditional", "The pivot is justified (Conditional = with strings)."),
            ("Needs Evidence", "Promising, but come back with more proof first."),
            ("Rejected", "Not justified by the evidence provided."),
            ("Random Change", "Looks like swapping ideas without evidence — flagged as such."),
        ],
    )
    pivots = db.list_pivots(None)
    pending = [p for p in pivots if p["status"] == "Submitted"]
    st.write(f"**{len(pending)} pending petition(s)**")
    if not pivots:
        st.info("No pivot petitions submitted yet.")
    for p in pivots:
        team = db.get_team(p["team_id"]) or {}
        with st.expander(f"[{p['status']}] {team.get('name','?')} · {p['proposed_change'][:50]}"):
            st.write(f"**Original assumption:** {p['original_assum']}")
            st.write(f"**Challenging evidence:** {p['challenge_evid']}")
            st.write(f"**Affected block:** {p['affected_block']}")
            st.write(f"**Proposed change:** {p['proposed_change']}")
            st.write(f"**Change cost:** ${p['change_cost']:,.0f}")
            st.write(f"**New assumptions:** {p['new_assumptions']}")
            st.write(f"**Evidence needed:** {p['evidence_needed']}")
            decision = st.selectbox(
                "Decision", content.PIVOT_DECISIONS, key=f"pdec_{p['id']}",
                help="Approved/Conditional = justified; NeedsEvidence = get more proof; "
                     "Rejected = not justified; RandomChange = unjustified idea-swap.")
            note = st.text_input(
                "Committee note", value=p["committee_note"] or "", key=f"pnote_{p['id']}",
                help="Your reasoning, shown to the team on their Pivot page.")
            charge = st.checkbox(
                "Charge the change cost on approval", value=True, key=f"pchg_{p['id']}",
                help="If ticked and you approve, the team's proposed change cost is deducted "
                     "from their capital.")
            if st.button("Record decision", key=f"pbtn_{p['id']}",
                         help="Save the decision (and charge the cost if applicable)."):
                db.decide_pivot(p["id"], decision, note)
                if decision in ("Approved", "Conditional") and charge and p["change_cost"]:
                    db.adjust_resources(p["team_id"], money=-p["change_cost"], kind="pivot",
                                        description="Pivot change cost", allow_negative=True)
                st.success("Decision recorded.")
                st.rerun()


# --------------------------------------------------------------------------- #
# Dashboard scoring
# --------------------------------------------------------------------------- #
def scoring():
    st.subheader("📊 Set Dashboard Scores")
    _guide(
        "Grade each team on ten performance dimensions, 0–100, once per round. These scores "
        "drive the student dashboard and — for three of them — the venture valuation. Hover any "
        "slider to see what that dimension means. Scores are stored per round, so you can track "
        "improvement over the semester.",
        steps=[
            "Pick the team and confirm the round.",
            "Set each dimension slider 0–100 (hover for its meaning).",
            "Click Save scores. The resulting valuation is shown below.",
        ],
        terms=[
            ("Dimension", "One quality being graded, e.g. Customer Insight or Evidence Strength."),
            ("Valuation drivers", "Evidence Strength, Business-Model Coherence, and Team "
             "Execution feed directly into the venture valuation."),
        ],
    )
    teams = db.list_teams()
    if not teams:
        st.info("No teams yet. Create teams on the Team Setup page first.")
        return
    team = st.selectbox("Team", teams, format_func=lambda t: t["name"],
                        help="Which team you're scoring.")
    current = db.latest_scores(team["id"])

    with st.form("score_form"):
        rnd = st.number_input(
            "Round", 1, 15, db.current_round(),
            help="Which round these scores are for. Scores are kept per round.")
        new_scores = {}
        for name, meaning in content.DASHBOARD_DIMENSIONS:
            new_scores[name] = st.slider(
                name, 0, 100, int(current.get(name, 50)),
                help=meaning, key=f"sc_{team['id']}_{name}")
        if st.form_submit_button("Save scores",
                                 help="Store these scores for the selected round."):
            for name, val in new_scores.items():
                db.set_score(team["id"], int(rnd), name, val)
            st.success("Scores saved.")
            st.rerun()

    val = logic.compute_valuation(team["id"])
    st.metric("Resulting valuation", f"${val['valuation']:,.0f}",
              help="Recomputed from the latest scores using the valuation formula.")


# --------------------------------------------------------------------------- #
# Value Proposition Auction oversight
# --------------------------------------------------------------------------- #
def vp_auction():
    st.subheader("💠 VP Auction Oversight")
    _guide(
        "In the Value Proposition Auction, teams bet Venture Tokens on their competing ideas "
        "and the app automatically taxes overconfidence and rewards evidence-based redirection. "
        "Your role here is quality control: teams set each proposition's evidence support "
        "themselves, and you can override any value that doesn't match the real evidence — which "
        "changes the tax and dividend they receive next round.",
        steps=[
            "Pick the team.",
            "Review each proposition and its self-reported evidence support.",
            "Override any value that's inflated or understated, then click Override.",
            "Check the auction results table to see their alignment, tax, and dividend history.",
        ],
        terms=[
            ("Evidence support", "0–10 rating of how well real evidence backs a proposition."),
            ("Alignment", "Tokens weighted by evidence support; higher means better-justified bets."),
            ("Tax / Dividend", "Auto-applied credit penalty (overconfidence) or reward (learning)."),
        ],
    )
    teams = db.list_teams()
    if not teams:
        st.info("No teams yet. Create teams on the Team Setup page first.")
        return
    team = st.selectbox("Team", teams, format_func=lambda t: t["name"],
                        help="Which team's auction to review.")

    props = db.list_value_props(team["id"])
    if not props:
        st.info("This team has not created any value propositions yet.")
    else:
        st.write("### Propositions & evidence support")
        st.caption("Override a rating to match the real evidence quality; it affects the next "
                   "auction's tax and dividend.")
        for p in props:
            c1, c2 = st.columns([3, 2])
            c1.write(f"**{p['name']}** — {p['tokens']} tokens")
            c1.caption(p["description"] or "")
            new_ev = c2.slider(
                "Evidence support", 0, 10, int(p["evidence_strength"]),
                key=f"iv_vpev_{p['id']}",
                help="Your assessment of how well evidence backs this proposition, 0–10. "
                     "Overriding here overrules the team's self-rating.")
            if c2.button("Override", key=f"iv_vpupd_{p['id']}",
                         help="Save your evidence-support rating for this proposition."):
                db.update_value_prop(p["id"], evidence_strength=new_ev)
                st.rerun()

    st.divider()
    st.write("### Auction results")
    results = db.list_vp_results(team["id"])
    if results:
        st.dataframe(
            [{"When": r["created_at"], "Round": r["round"], "Tokens": r["total_tokens"],
              "Alignment": r["alignment"], "Prev": r["prev_alignment"],
              "Tax": r["tax"], "Dividend": r["dividend"], "Net": r["net_credits"]}
             for r in results],
            use_container_width=True, hide_index=True,
        )
    else:
        st.caption("No auction rounds run yet.")


# --------------------------------------------------------------------------- #
# Cohort overview & submissions
# --------------------------------------------------------------------------- #
def overview():
    st.subheader("🗺️ Cohort Overview")
    _guide(
        "Your at-a-glance view of every team: resources, valuation, evidence, and risk in one "
        "table. Use it to spot teams coasting on weak evidence or ignoring big risks. Below the "
        "table is a reminder of the multiple recognition categories (so one lucky idea can't "
        "dominate) and a per-team inspector for their canvases, assumptions, experiments, and "
        "reflections. Nothing to enter here — it's read-only.",
        terms=[
            ("Valuation", "The team's current simulated venture value."),
            ("Behavioral", "Count of strong (behavior-based) evidence items."),
            ("High-risk untested", "Important assumptions with no evidence — a red flag."),
            ("Recognition dimensions", "The several ways teams can 'win,' beyond raw score."),
        ],
    )
    teams = db.list_teams()
    if not teams:
        st.info("No teams yet. Create teams on the Team Setup page first.")
        return
    rows = []
    for t in teams:
        val = logic.compute_valuation(t["id"])
        esum = logic.evidence_summary(t["id"])
        arep = logic.assumption_risk_report(t["id"])
        eff = logic.experiment_efficiency(t["id"])
        rows.append({
            "Team": t["name"], "Stage": t["stage"], "Capital": f"${t['capital']:,.0f}",
            "Credits": round(t["evidence_credits"], 1), "Valuation": f"${val['valuation']:,.0f}",
            "Evidence items": esum["count"], "Behavioral": esum["behavioral"],
            "High-risk untested": len(arep["exposed"]), "Experiments": eff["experiments"],
        })
    st.dataframe(rows, use_container_width=True, hide_index=True)

    st.divider()
    st.write("### Recognition dimensions")
    st.caption("The winner is not the highest simulated profit. Recognize across dimensions.")
    st.write(
        "- Strongest evidence-based venture\n- Most improved business model\n"
        "- Best customer insight\n- Most disciplined experiment portfolio\n"
        "- Best responsible pivot\n- Highest investor confidence\n- Best overall venture performance"
    )

    st.divider()
    st.write("### Submissions & artifacts")
    st.caption("Pick a team to inspect what they've produced across the four artifact types.")
    team = st.selectbox("Inspect team", teams, format_func=lambda t: t["name"], key="ov_team",
                        help="Which team's submitted work to review.")
    tab1, tab2, tab3, tab4 = st.tabs(["Canvases", "Assumptions", "Experiments", "Reflections"])
    with tab1:
        for c in db.list_canvases(team["id"]):
            st.write(f"**{c['ctype']} v{c['version']}** · {c['label']} · {c['created_at']}")
            if c["note"]:
                st.caption(c["note"])
    with tab2:
        for a in db.list_assumptions(team["id"]):
            st.write(f"- [{a['status']}] {a['text']} ({a['risk_type']}, importance {a['importance']})")
    with tab3:
        for e in db.list_experiments(team["id"]):
            st.write(f"- [{e['outcome']}] {e['card_type']}: {e['hypothesis'][:70]}")
    with tab4:
        for r in db.list_reflections(team["id"]):
            st.write(f"- {r['student_name']} (R{r['round']}): {r['contribution'][:80]}")
