"""
views_student.py — Student/team-facing screens for Venture Foundry.
"""

import streamlit as st

import db
import content
import logic


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _resource_bar(team):
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Capital", f"${team['capital']:,.0f}")
    c2.metric("Evidence Credits", f"{team['evidence_credits']:,.1f}")
    c3.metric("Founder-hours", f"{team['founder_hours']:,.0f}")
    c4.metric("Venture Tokens", f"{team['venture_tokens']}")


def _refresh_team(team_id):
    return db.get_team(team_id)


# --------------------------------------------------------------------------- #
# Dashboard
# --------------------------------------------------------------------------- #
def dashboard(team):
    st.subheader(f"🏭 {team['name']} — Venture Dashboard")
    st.caption(f"Stage: **{team['stage']}**  ·  Round {db.current_round()}  ·  "
               f"Join code `{team['join_code']}`")
    _resource_bar(team)

    val = logic.compute_valuation(team["id"])
    st.divider()
    vc1, vc2 = st.columns([1, 2])
    with vc1:
        st.metric("Venture Valuation", f"${val['valuation']:,.0f}")
        st.caption("Potential × Evidence × Coherence × Execution − Risk")
    with vc2:
        st.write("**Valuation components**")
        st.write(
            f"- Market potential: ${val['market_potential']:,.0f}\n"
            f"- Evidence confidence: ×{val['evidence_confidence']}\n"
            f"- Business-model coherence: ×{val['bm_coherence']}\n"
            f"- Execution factor: ×{val['execution_factor']}\n"
            f"- Unresolved-risk penalty: −${val['unresolved_risk']:,.0f}"
        )

    st.divider()
    st.write("### Performance dimensions")
    scores = db.latest_scores(team["id"])
    if not scores:
        st.info("No dashboard scores yet — the Venture Foundry Director sets these each round.")
    else:
        for name, meaning in content.DASHBOARD_DIMENSIONS:
            s = scores.get(name)
            cols = st.columns([2, 5, 1])
            cols[0].write(f"**{name}**")
            cols[1].progress(int(s) if s is not None else 0)
            cols[2].write(f"{s:.0f}" if s is not None else "—")
            cols[1].caption(meaning)

    st.divider()
    esum = logic.evidence_summary(team["id"])
    arep = logic.assumption_risk_report(team["id"])
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Evidence items", esum["count"])
    m2.metric("Behavioral evidence", esum["behavioral"])
    m3.metric("Assumptions untested", arep["untested"])
    m4.metric("High-risk untested", len(arep["exposed"]))
    if arep["exposed"]:
        st.warning(
            "⚠️ High-importance assumptions with no evidence — these can invalidate the "
            "venture if they fail:\n\n"
            + "\n".join(f"- {a['text']} ({a['risk_type']})" for a in arep["exposed"])
        )

    with st.expander("Transaction ledger"):
        txns = db.list_transactions(team["id"], limit=50)
        if txns:
            st.dataframe(
                [{"When": t["created_at"], "Kind": t["kind"], "$": t["money"],
                  "Credits": t["credits"], "Hours": t["hours"], "Note": t["description"]}
                 for t in txns],
                use_container_width=True, hide_index=True,
            )
        else:
            st.caption("No transactions yet.")


# --------------------------------------------------------------------------- #
# Founder & Opportunity
# --------------------------------------------------------------------------- #
def founder_opportunity(team):
    st.subheader("🧭 Founder & Opportunity Formation")
    st.caption("You do not start with a product. You start with a territory and a "
               "set of founder capabilities and constraints.")

    card = db.get_founder_card(team["id"])
    st.write("### Your founder card")
    if card:
        st.info(
            f"**{card.get('name','—')}**\n\n"
            f"- Skills: {card.get('skills','—')}\n"
            f"- Networks: {card.get('networks','—')}\n"
            f"- Budget you can afford to lose: ${card.get('budget','—')}\n"
            f"- Founder-hours available: {card.get('hours','—')}\n"
            f"- Risk tolerance: {card.get('risk','—')}\n"
            f"- Ethical boundary: {card.get('ethics','—')}"
        )
    else:
        st.caption("The Director has not yet assigned a founder card.")

    st.write(f"### Opportunity territory\n**{team['opportunity'] or '—'}**")

    st.divider()
    st.write("### Candidate ventures")
    st.caption("Generate at least three possible ventures and compare them before "
               "committing. Opportunity selection is a constrained decision, not free brainstorming.")

    ventures = db.get_ventures(team["id"])
    for i, v in enumerate(ventures):
        with st.expander(f"Venture {i+1}: {v.get('name','(unnamed)')}"):
            st.write(f"**Customer importance:** {v.get('importance','—')}/5")
            st.write(f"**Founder–opportunity fit:** {v.get('fit','—')}/5")
            st.write(f"**Access to customers:** {v.get('access','—')}/5")
            st.write(f"**Evidence availability:** {v.get('evidence','—')}/5")
            st.write(f"**Experiment affordability:** {v.get('afford','—')}/5")
            st.write(f"**Notes:** {v.get('notes','')}")
            if st.button("Remove", key=f"rmv_{i}"):
                ventures.pop(i)
                db.set_ventures(team["id"], ventures)
                st.rerun()

    with st.form("add_venture", clear_on_submit=True):
        st.write("**Add a candidate venture**")
        name = st.text_input("Venture name / one-line description")
        c1, c2, c3 = st.columns(3)
        importance = c1.slider("Customer importance", 1, 5, 3)
        fit = c2.slider("Founder–opportunity fit", 1, 5, 3)
        access = c3.slider("Access to customers", 1, 5, 3)
        c4, c5 = st.columns(2)
        evidence = c4.slider("Evidence availability", 1, 5, 3)
        afford = c5.slider("Experiment affordability", 1, 5, 3)
        notes = st.text_area("Notes")
        if st.form_submit_button("Add venture") and name:
            ventures.append({"name": name, "importance": importance, "fit": fit,
                             "access": access, "evidence": evidence, "afford": afford,
                             "notes": notes})
            db.set_ventures(team["id"], ventures)
            st.success("Venture added.")
            st.rerun()


# --------------------------------------------------------------------------- #
# Canvases (versioned)
# --------------------------------------------------------------------------- #
_CANVAS_DEFS = {
    "customer_profile": ("Customer Profile", content.CUSTOMER_PROFILE_BLOCKS),
    "vpc": ("Value Proposition Canvas", content.VPC_BLOCKS),
    "bmc": ("Business Model Canvas", content.BMC_BLOCKS),
}


def canvases(team):
    st.subheader("🗂️ Canvases")
    st.caption("Every canvas begins as a collection of hypotheses. Save dated "
               "versions so learning is visible over time.")

    ctype = st.selectbox(
        "Canvas type",
        list(_CANVAS_DEFS.keys()),
        format_func=lambda k: _CANVAS_DEFS[k][0],
    )
    title, blocks = _CANVAS_DEFS[ctype]

    existing = db.list_canvases(team["id"], ctype)
    latest = existing[-1] if existing else None

    st.write(f"### {title}")
    if existing:
        st.caption(f"{len(existing)} version(s) saved. Editing starts from the latest.")

    with st.form(f"canvas_{ctype}", clear_on_submit=False):
        data = {}
        for key, label, hint in blocks:
            prefill = latest["data"].get(key, "") if latest else ""
            data[key] = st.text_area(f"{label} — {hint}", value=prefill, key=f"{ctype}_{key}")
        label = st.text_input("Version label (optional)",
                              value=f"{title} v{len(existing)+1}")
        note = st.text_input("What changed / why (evidence-driven?)")
        if st.form_submit_button(f"Save new {title} version"):
            v = db.save_canvas(team["id"], ctype, data, label, note)
            st.success(f"Saved {title} version {v}.")
            st.rerun()

    if existing:
        st.divider()
        st.write("### Version history")
        for cv in reversed(existing):
            with st.expander(f"v{cv['version']} · {cv['label']} · {cv['created_at']}"):
                if cv["note"]:
                    st.caption(f"Change note: {cv['note']}")
                for key, label, _ in blocks:
                    st.markdown(f"**{label}**")
                    st.write(cv["data"].get(key) or "_(empty)_")


# --------------------------------------------------------------------------- #
# Assumption map / market
# --------------------------------------------------------------------------- #
def assumptions(team):
    st.subheader("🎯 Assumption Map & Market")
    st.caption("Convert every element of the venture into a testable assumption. "
               "An untested high-importance assumption that later proves false costs you dearly.")

    with st.form("add_assumption", clear_on_submit=True):
        text = st.text_input("Assumption (state it as something that must be true)")
        c1, c2, c3, c4 = st.columns(4)
        risk = c1.selectbox("Risk type", content.RISK_TYPES)
        importance = c2.slider("Importance", 1, 5, 3)
        evidence_level = c3.slider("Existing evidence", 1, 5, 1)
        testability = c4.slider("Testability", 1, 5, 3)
        if st.form_submit_button("Add assumption") and text:
            db.add_assumption(team["id"], text, risk, importance, evidence_level, testability)
            st.success("Assumption added.")
            st.rerun()

    assums = db.list_assumptions(team["id"])
    if not assums:
        st.info("No assumptions yet.")
        return

    st.divider()
    st.write("### Prioritization — importance vs. evidence")
    st.caption("Top priority: high importance, low existing evidence.")
    for a in assums:
        priority = a["importance"] * (6 - a["evidence_level"])
        with st.expander(
            f"[{a['status']}] {a['text']}  ·  {a['risk_type']}  ·  priority {priority}"
        ):
            c1, c2, c3 = st.columns(3)
            c1.write(f"Importance: {a['importance']}/5")
            c2.write(f"Existing evidence: {a['evidence_level']}/5")
            c3.write(f"Testability: {a['testability']}/5")
            new_status = st.selectbox(
                "Status", ["Untested", "Testing", "Supported", "Refuted", "Ignored"],
                index=["Untested", "Testing", "Supported", "Refuted", "Ignored"].index(a["status"]),
                key=f"astatus_{a['id']}",
            )
            cc1, cc2 = st.columns(2)
            if cc1.button("Update status", key=f"aupd_{a['id']}"):
                db.update_assumption(a["id"], status=new_status)
                st.rerun()
            if cc2.button("Delete", key=f"adel_{a['id']}"):
                db.delete_assumption(a["id"])
                st.rerun()


# --------------------------------------------------------------------------- #
# Experiment marketplace
# --------------------------------------------------------------------------- #
def experiments(team):
    st.subheader("🧪 Experiment Marketplace")
    st.caption("Purchase experiment cards with limited resources, then specify success "
               "and failure thresholds BEFORE you see results.")
    team = _refresh_team(team["id"])
    _resource_bar(team)

    assums = db.list_assumptions(team["id"])
    if not assums:
        st.warning("Add assumptions first — every experiment tests a specific assumption.")
    st.divider()

    st.write("### Buy & design an experiment")
    card_name = st.selectbox("Experiment card", [c["name"] for c in content.EXPERIMENT_CARDS])
    card = content.EXPERIMENT_CARD_MAP[card_name]
    ic1, ic2, ic3, ic4 = st.columns(4)
    ic1.metric("Money", f"${card['money']}")
    ic2.metric("Hours", f"{card['hours']}")
    ic3.metric("Credits", f"{card['credits']}")
    ic4.metric("Evidence strength", f"{card['strength']}/10")
    st.caption(f"Best for **{card['suits']}** assumptions · Min sample: {card['sample']} · "
               f"Watch for bias: {card['bias']}")

    with st.form("buy_experiment", clear_on_submit=True):
        if assums:
            assum_id = st.selectbox(
                "Assumption tested",
                [a["id"] for a in assums],
                format_func=lambda i: next(a["text"] for a in assums if a["id"] == i),
            )
        else:
            assum_id = None
        hypothesis = st.text_area(
            "Hypothesis",
            placeholder="We believe independent coffee shops will pay $49/mo for automated inventory forecasting.",
        )
        metric = st.text_input("Metric", placeholder="Number of shop owners requesting a trial")
        c1, c2 = st.columns(2)
        success = c1.text_input("Success threshold",
                                placeholder="≥5 request a trial and ≥2 share sales data")
        failure = c2.text_input("Failure threshold", placeholder="≤1 requests a trial")
        decision = st.text_input("Decision rule",
                                 placeholder="If supported, build clickable prototype; if refuted, revisit segment")
        submitted = st.form_submit_button("Purchase & design experiment")
        if submitted:
            if assum_id is None:
                st.error("Add an assumption to test first.")
            elif not hypothesis or not success or not failure:
                st.error("Hypothesis, success threshold, and failure threshold are required.")
            else:
                ok, msg, _ = logic.purchase_experiment(
                    team["id"], card, assum_id, hypothesis, metric, success, failure, decision)
                if ok:
                    db.update_assumption(assum_id, status="Testing")
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

    st.divider()
    st.write("### Your experiments")
    exps = db.list_experiments(team["id"])
    if not exps:
        st.caption("No experiments yet.")
    for e in exps:
        with st.expander(f"[{e['outcome']}] {e['card_type']} — {e['hypothesis'][:60]}"):
            st.write(f"**Metric:** {e['metric']}")
            st.write(f"**Success threshold:** {e['success_threshold']}")
            st.write(f"**Failure threshold:** {e['failure_threshold']}")
            st.write(f"**Decision rule:** {e['decision_rule']}")
            st.write(f"**Cost:** ${e['cost_money']} · {e['cost_time']}h · {e['cost_credits']} credits · "
                     f"strength {e['evidence_strength']}/10")
            result = st.text_area("Record result", value=e["result"] or "", key=f"res_{e['id']}")
            outcome = st.selectbox(
                "Outcome", ["Designed", "Running", "Supported", "Refuted", "Inconclusive"],
                index=["Designed", "Running", "Supported", "Refuted", "Inconclusive"].index(e["outcome"]),
                key=f"outc_{e['id']}",
            )
            if st.button("Save result", key=f"saveres_{e['id']}"):
                db.update_experiment(e["id"], result=result, outcome=outcome)
                if e["assumption_id"] and outcome in ("Supported", "Refuted"):
                    db.update_assumption(e["assumption_id"], status=outcome)
                st.success("Saved.")
                st.rerun()


# --------------------------------------------------------------------------- #
# Evidence ledger
# --------------------------------------------------------------------------- #
def evidence(team):
    st.subheader("📒 Evidence Ledger")
    st.caption("Behavioral evidence outranks opinion. Logging evidence earns Evidence "
               "Credits proportional to its strength on the ladder.")

    with st.expander("Evidence-strength ladder"):
        st.table([{"Evidence": lbl, "Value": val} for lbl, val in content.EVIDENCE_LADDER])

    assums = db.list_assumptions(team["id"])
    with st.form("add_evidence", clear_on_submit=True):
        description = st.text_input("What did you learn? (one line)")
        etype = st.selectbox("Evidence type", [lbl for lbl, _ in content.EVIDENCE_LADDER])
        source = st.text_input("Source", placeholder="e.g., Interview with 3 coffee-shop owners")
        if assums:
            assum_id = st.selectbox(
                "Related assumption (optional)",
                [None] + [a["id"] for a in assums],
                format_func=lambda i: "—" if i is None else next(a["text"] for a in assums if a["id"] == i),
            )
        else:
            assum_id = None
        if st.form_submit_button("Log evidence") and description:
            award, strength = logic.log_evidence_and_award(
                team["id"], description, etype, source, assum_id)
            st.success(f"Logged. Strength {strength}/10 → earned {award} Evidence Credits.")
            st.rerun()

    st.divider()
    esum = logic.evidence_summary(team["id"])
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Items", esum["count"])
    c2.metric("Avg strength", esum["avg_strength"])
    c3.metric("Behavioral", esum["behavioral"])
    c4.metric("Opinion-only", esum["opinion"])

    ev = db.list_evidence(team["id"])
    if ev:
        st.dataframe(
            [{"When": e["created_at"], "Learning": e["description"], "Type": e["evidence_type"],
              "Strength": e["strength"], "Credits": e["credits_award"], "Source": e["source"]}
             for e in ev],
            use_container_width=True, hide_index=True,
        )


# --------------------------------------------------------------------------- #
# Value Proposition Auction
# --------------------------------------------------------------------------- #
def vp_auction(team):
    st.subheader("💠 Value Proposition Auction")
    st.caption(
        f"Field at least {content.MIN_VALUE_PROPS} competing value propositions for the "
        f"same customer segment, then privately allocate {content.VENTURE_TOKEN_POOL} "
        "Venture Tokens. Allocation reveals your confidence — but evidence decides "
        "whether it pays off."
    )
    st.info(
        "**How the round scores automatically:**\n"
        "- *Alignment* = your tokens weighted by each proposition's evidence support.\n"
        f"- **Overconfidence Tax** — up to {int(content.OVERCONFIDENCE_TAX_MAX)} credits when "
        "tokens sit on weakly-supported propositions.\n"
        f"- **Learning Dividend** — up to {int(content.LEARNING_DIVIDEND_MAX)} credits when you "
        "redirect tokens toward better-supported propositions vs. your last auction."
    )

    props = db.list_value_props(team["id"])

    # ---- Manage propositions -------------------------------------------------
    st.write("### Your value propositions")
    st.caption("Set each proposition's evidence support (0–10) to reflect your evidence "
               "ledger. The Director can override this to match real evidence quality.")
    for p in props:
        with st.expander(f"{p['name']}  ·  evidence {p['evidence_strength']}/10  ·  "
                         f"{p['tokens']} tokens"):
            st.write(p["description"] or "_(no description)_")
            new_ev = st.slider("Evidence support", 0, 10, int(p["evidence_strength"]),
                               key=f"vpev_{p['id']}")
            c1, c2 = st.columns(2)
            if c1.button("Update evidence", key=f"vpupd_{p['id']}"):
                db.update_value_prop(p["id"], evidence_strength=new_ev)
                st.rerun()
            if c2.button("Delete", key=f"vpdel_{p['id']}"):
                db.delete_value_prop(p["id"])
                st.rerun()

    with st.form("add_vp", clear_on_submit=True):
        st.write("**Add a value proposition**")
        name = st.text_input("Name")
        desc = st.text_area("Products/services · pain relievers · gain creators")
        ev = st.slider("Evidence support (0–10)", 0, 10, 0)
        if st.form_submit_button("Add proposition") and name:
            db.add_value_prop(team["id"], name, desc, ev)
            st.rerun()

    if len(props) < content.MIN_VALUE_PROPS:
        st.warning(f"Add at least {content.MIN_VALUE_PROPS} propositions to run the auction "
                   f"(you have {len(props)}).")
        return

    # ---- Allocate tokens -----------------------------------------------------
    st.divider()
    st.write(f"### Allocate {content.VENTURE_TOKEN_POOL} Venture Tokens")
    allocations = {}
    cols = st.columns(min(len(props), 4))
    for i, p in enumerate(props):
        with cols[i % len(cols)]:
            allocations[p["id"]] = st.number_input(
                p["name"], min_value=0, max_value=content.VENTURE_TOKEN_POOL,
                value=int(p["tokens"]), step=5, key=f"vptok_{p['id']}")
    total = sum(allocations.values())
    remaining = content.VENTURE_TOKEN_POOL - total
    (st.error if remaining < 0 else st.caption)(
        f"Allocated {total} / {content.VENTURE_TOKEN_POOL} · {remaining} remaining")

    preview = logic.preview_vp_auction(team["id"], allocations)
    if preview.get("ok"):
        pc1, pc2, pc3, pc4 = st.columns(4)
        pc1.metric("Alignment", preview["alignment"])
        pc2.metric("Overconfidence Tax", f"-{preview['tax']}")
        pc3.metric("Learning Dividend", f"+{preview['dividend']}")
        pc4.metric("Net credits", preview["net"])
        st.caption("Preview only — nothing is charged until you submit.")
        if st.button("Submit auction round", type="primary"):
            res = logic.run_vp_auction(team["id"], allocations, db.current_round())
            if res.get("committed"):
                st.success(f"Auction resolved. Net change: {res['net']} Evidence Credits "
                           f"(tax {res['tax']}, dividend {res['dividend']}).")
                st.rerun()
            else:
                st.error(res.get("reason", "Could not run auction."))
    else:
        st.info(preview.get("reason", ""))

    # ---- History -------------------------------------------------------------
    results = db.list_vp_results(team["id"])
    if results:
        st.divider()
        st.write("### Auction history")
        st.dataframe(
            [{"When": r["created_at"], "Round": r["round"], "Tokens": r["total_tokens"],
              "Alignment": r["alignment"], "Prev": r["prev_alignment"],
              "Tax": r["tax"], "Dividend": r["dividend"], "Net": r["net_credits"]}
             for r in results],
            use_container_width=True, hide_index=True,
        )


# --------------------------------------------------------------------------- #
# Market events
# --------------------------------------------------------------------------- #
def market_events(team):
    st.subheader("📡 Market Events")
    st.caption("Events are not random punishments — each one exposes an assumption in "
               "your canvas. Respond while keeping the model coherent.")
    evs = db.list_events(team["id"])
    if not evs:
        st.info("No market events yet.")
        return
    for e in evs:
        scope = "All teams" if e["team_id"] is None else "Your team"
        icon = "✅" if e["resolved"] else "🔔"
        with st.expander(f"{icon} Round {e['round']} · {e['category']} · {scope}"):
            st.write(f"**Event:** {e['text']}")
            if e["exposes"]:
                st.caption(f"Assumption exposed: {e['exposes']}")


# --------------------------------------------------------------------------- #
# Pivot petition
# --------------------------------------------------------------------------- #
def pivots(team):
    st.subheader("🔀 Pivot Petition")
    st.caption("A pivot is a disciplined response to learning — not simply replacing a "
               "failing idea. Submit a formal petition for committee review.")

    with st.form("pivot_form", clear_on_submit=True):
        original = st.text_area("Original assumption")
        challenge = st.text_area("Evidence that challenged it")
        block = st.text_input("Value Proposition / Business Model block affected")
        change = st.text_area("Proposed change")
        cost = st.number_input("Cost of the change ($)", min_value=0.0, value=0.0, step=50.0)
        new_assums = st.text_area("New assumptions this creates")
        needed = st.text_area("Evidence required to support the new direction")
        if st.form_submit_button("Submit pivot petition"):
            if not original or not change:
                st.error("Original assumption and proposed change are required.")
            else:
                db.add_pivot(team["id"], {
                    "original_assum": original, "challenge_evid": challenge,
                    "affected_block": block, "proposed_change": change,
                    "change_cost": cost, "new_assumptions": new_assums,
                    "evidence_needed": needed,
                })
                st.success("Petition submitted to the investment committee.")
                st.rerun()

    st.divider()
    st.write("### Your petitions")
    for p in db.list_pivots(team["id"]):
        with st.expander(f"[{p['status']}] {p['proposed_change'][:60]} · {p['created_at']}"):
            st.write(f"**Original assumption:** {p['original_assum']}")
            st.write(f"**Challenging evidence:** {p['challenge_evid']}")
            st.write(f"**Affected block:** {p['affected_block']}")
            st.write(f"**Proposed change:** {p['proposed_change']}")
            st.write(f"**Change cost:** ${p['change_cost']:,.0f}")
            st.write(f"**New assumptions:** {p['new_assumptions']}")
            st.write(f"**Evidence needed:** {p['evidence_needed']}")
            if p["committee_note"]:
                st.info(f"Committee: {p['committee_note']}")


# --------------------------------------------------------------------------- #
# Reflections (individual accountability)
# --------------------------------------------------------------------------- #
def reflections(team):
    st.subheader("📝 Entrepreneurial Decision Journal")
    st.caption("Individual reflection converts activity into learning and protects "
               "against free riding.")

    with st.form("reflection_form", clear_on_submit=True):
        name = st.text_input("Your name")
        rnd = st.number_input("Round", min_value=1, max_value=15, value=db.current_round())
        expected = st.text_area("What did we expect?")
        occurred = st.text_area("What occurred?")
        assumption = st.text_area("Which assumption shaped our decision?")
        overlooked = st.text_area("What evidence did we overlook?")
        differently = st.text_area("What would we do differently?")
        contribution = st.text_area("What did I personally contribute?")
        if st.form_submit_button("Submit reflection"):
            if not name:
                st.error("Name is required.")
            else:
                db.add_reflection(team["id"], {
                    "student_name": name, "round": int(rnd), "expected": expected,
                    "occurred": occurred, "assumption": assumption, "overlooked": overlooked,
                    "differently": differently, "contribution": contribution,
                })
                st.success("Reflection submitted.")
                st.rerun()

    st.divider()
    refs = db.list_reflections(team["id"])
    if refs:
        st.write(f"### {len(refs)} reflection(s) on record")
        for r in refs:
            with st.expander(f"{r['student_name']} · Round {r['round']} · {r['created_at']}"):
                st.write(f"**Expected:** {r['expected']}")
                st.write(f"**Occurred:** {r['occurred']}")
                st.write(f"**Assumption:** {r['assumption']}")
                st.write(f"**Overlooked:** {r['overlooked']}")
                st.write(f"**Differently:** {r['differently']}")
                st.write(f"**My contribution:** {r['contribution']}")
