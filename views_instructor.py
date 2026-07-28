"""
views_instructor.py — Venture Foundry Director (instructor) console.
"""

import random

import streamlit as st

import db
import content
import logic


# --------------------------------------------------------------------------- #
# Round control & semester map
# --------------------------------------------------------------------------- #
def round_control():
    st.subheader("🎛️ Round & Semester Control")
    cur = db.current_round()
    c1, c2 = st.columns([1, 3])
    with c1:
        new_round = st.number_input("Current round", 1, 15, cur)
        if st.button("Set round"):
            db.set_setting("current_round", int(new_round))
            st.success(f"Round set to {new_round}.")
            st.rerun()
    with c2:
        pin = st.text_input("Instructor PIN (change)", value=db.get_setting("instructor_pin", "foundry"))
        if st.button("Update PIN"):
            db.set_setting("instructor_pin", pin)
            st.success("PIN updated.")

    st.divider()
    st.write("### 15-week semester map")
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
    st.caption("Create teams, assign a territory and founder card, and set starting resources.")

    with st.form("create_team", clear_on_submit=True):
        name = st.text_input("Team name")
        c1, c2 = st.columns(2)
        opportunity = c1.selectbox("Opportunity territory", content.OPPORTUNITY_TERRITORIES)
        card_name = c2.selectbox("Founder card", [c["name"] for c in content.FOUNDER_CARDS])
        card = next(c for c in content.FOUNDER_CARDS if c["name"] == card_name)
        c3, c4, c5, c6 = st.columns(4)
        capital = c3.number_input("Starting capital $", 0, 100000, int(card["budget"]))
        credits = c4.number_input("Evidence Credits", 0, 1000, 10)
        hours = c5.number_input("Founder-hours", 0, 1000, int(card["hours"]))
        potential = c6.number_input("Market potential $", 0, 100000000, 1000000, step=100000)
        if st.form_submit_button("Create team") and name:
            code = db.create_team(name, opportunity, card, capital, credits, hours, potential)
            st.success(f"Team '{name}' created. Join code: **{code}**")
            st.rerun()

    st.divider()
    st.write("### Teams")
    teams = db.list_teams()
    if not teams:
        st.info("No teams yet.")
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
            )
            new_risk = st.number_input("Unresolved-risk penalty $", 0, 10000000,
                                       int(t["unresolved_risk"]), step=25000, key=f"risk_{t['id']}")
            c1, c2 = st.columns(2)
            if c1.button("Save", key=f"savet_{t['id']}"):
                db.update_team(t["id"], stage=new_stage, unresolved_risk=new_risk)
                st.success("Saved.")
                st.rerun()
            if c2.button("Delete team", key=f"delt_{t['id']}"):
                db.delete_team(t["id"])
                st.rerun()


# --------------------------------------------------------------------------- #
# Resources (grant / deduct)
# --------------------------------------------------------------------------- #
def resources():
    st.subheader("💰 Grant / Deduct Resources")
    teams = db.list_teams()
    if not teams:
        st.info("No teams yet.")
        return
    team = st.selectbox("Team", teams, format_func=lambda t: t["name"])
    c1, c2, c3 = st.columns(3)
    c1.metric("Capital", f"${team['capital']:,.0f}")
    c2.metric("Evidence Credits", f"{team['evidence_credits']:.1f}")
    c3.metric("Founder-hours", f"{team['founder_hours']:.0f}")

    with st.form("adjust_res", clear_on_submit=True):
        cc1, cc2, cc3 = st.columns(3)
        money = cc1.number_input("Δ Capital $", -100000, 100000, 0, step=100)
        credits = cc2.number_input("Δ Evidence Credits", -1000, 1000, 0)
        hours = cc3.number_input("Δ Founder-hours", -1000, 1000, 0)
        desc = st.text_input("Reason", placeholder="Investor round, funding request, penalty…")
        if st.form_submit_button("Apply adjustment"):
            ok, msg = db.adjust_resources(team["id"], money=money, credits=credits, hours=hours,
                                          kind="director", description=desc, allow_negative=True)
            st.success("Applied.") if ok else st.error(msg)
            st.rerun()


# --------------------------------------------------------------------------- #
# Market events
# --------------------------------------------------------------------------- #
def events():
    st.subheader("📡 Issue Market Events")
    st.caption("Beginning Week 7, introduce one event per round. Each should expose an "
               "assumption embedded in a team's canvas.")
    teams = db.list_teams()

    with st.form("issue_event", clear_on_submit=True):
        category = st.selectbox("Category", list(content.MARKET_EVENTS.keys()))
        options = content.MARKET_EVENTS[category]
        idx = st.selectbox("Event", range(len(options)),
                           format_func=lambda i: options[i][0])
        text, exposes = options[idx]
        st.caption(f"Exposes assumption: {exposes}")
        target = st.selectbox(
            "Target", ["All teams (broadcast)"] + [t["name"] for t in teams])
        rnd = st.number_input("Round", 1, 15, db.current_round())
        if st.form_submit_button("Issue event"):
            if target == "All teams (broadcast)":
                db.add_event(None, int(rnd), category, text, exposes)
            else:
                tid = next(t["id"] for t in teams if t["name"] == target)
                db.add_event(tid, int(rnd), category, text, exposes)
            st.success("Event issued.")
            st.rerun()

    if st.button("🎲 Issue a random event to all teams"):
        cat = random.choice(list(content.MARKET_EVENTS.keys()))
        text, exposes = random.choice(content.MARKET_EVENTS[cat])
        db.add_event(None, db.current_round(), cat, text, exposes)
        st.success(f"Random {cat} event issued.")
        st.rerun()

    st.divider()
    st.write("### Event history")
    for e in db.list_events(None):
        scope = "All" if e["team_id"] is None else (db.get_team(e["team_id"]) or {}).get("name", "?")
        st.write(f"- R{e['round']} · **{e['category']}** · {scope} · {e['text']}")


# --------------------------------------------------------------------------- #
# Pivot committee
# --------------------------------------------------------------------------- #
def pivot_committee():
    st.subheader("⚖️ Pivot Committee")
    st.caption("Approve, approve conditionally, request more evidence, reject, or "
               "classify as random change rather than evidence-based learning.")
    pivots = db.list_pivots(None)
    pending = [p for p in pivots if p["status"] == "Submitted"]
    st.write(f"**{len(pending)} pending petition(s)**")
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
            decision = st.selectbox("Decision", content.PIVOT_DECISIONS, key=f"pdec_{p['id']}")
            note = st.text_input("Committee note", value=p["committee_note"] or "", key=f"pnote_{p['id']}")
            charge = st.checkbox("Charge the change cost on approval", value=True, key=f"pchg_{p['id']}")
            if st.button("Record decision", key=f"pbtn_{p['id']}"):
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
    st.caption("Score each dimension 0–100. Evidence Strength, Business-Model Coherence, "
               "and Team Execution feed the venture valuation.")
    teams = db.list_teams()
    if not teams:
        st.info("No teams yet.")
        return
    team = st.selectbox("Team", teams, format_func=lambda t: t["name"])
    current = db.latest_scores(team["id"])

    with st.form("score_form"):
        rnd = st.number_input("Round", 1, 15, db.current_round())
        new_scores = {}
        for name, meaning in content.DASHBOARD_DIMENSIONS:
            new_scores[name] = st.slider(name, 0, 100, int(current.get(name, 50)),
                                         help=meaning, key=f"sc_{team['id']}_{name}")
        if st.form_submit_button("Save scores"):
            for name, val in new_scores.items():
                db.set_score(team["id"], int(rnd), name, val)
            st.success("Scores saved.")
            st.rerun()

    val = logic.compute_valuation(team["id"])
    st.metric("Resulting valuation", f"${val['valuation']:,.0f}")


# --------------------------------------------------------------------------- #
# Value Proposition Auction oversight
# --------------------------------------------------------------------------- #
def vp_auction():
    st.subheader("💠 VP Auction Oversight")
    st.caption("Teams allocate Venture Tokens across competing propositions; the app "
               "auto-applies the Overconfidence Tax and Learning Dividend. Override a "
               "proposition's evidence support here to match the real evidence quality.")
    teams = db.list_teams()
    if not teams:
        st.info("No teams yet.")
        return
    team = st.selectbox("Team", teams, format_func=lambda t: t["name"])

    props = db.list_value_props(team["id"])
    if not props:
        st.info("This team has not created any value propositions yet.")
    else:
        st.write("### Propositions & evidence support")
        for p in props:
            c1, c2 = st.columns([3, 2])
            c1.write(f"**{p['name']}** — {p['tokens']} tokens")
            c1.caption(p["description"] or "")
            new_ev = c2.slider("Evidence support", 0, 10, int(p["evidence_strength"]),
                               key=f"iv_vpev_{p['id']}")
            if c2.button("Override", key=f"iv_vpupd_{p['id']}"):
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
    teams = db.list_teams()
    if not teams:
        st.info("No teams yet.")
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
    team = st.selectbox("Inspect team", teams, format_func=lambda t: t["name"], key="ov_team")
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
