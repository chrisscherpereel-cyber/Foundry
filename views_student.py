"""
views_student.py — Student/team-facing screens for Venture Foundry.

Every screen is written to be self-explanatory: a "How this page works" panel
sits at the top, and every input carries a hover-help (ⓘ) tooltip so a first-time
user can run the simulation without an instruction manual.
"""

import streamlit as st

import db
import content
import logic


# --------------------------------------------------------------------------- #
# Shared guidance helpers
# --------------------------------------------------------------------------- #
def _guide(what, steps=None, terms=None, expanded=False):
    """Render a plain-language 'How this page works' panel.

    what   — one-paragraph explanation of the page's purpose.
    steps  — optional list of do-this-now steps.
    terms  — optional list of (term, definition) tuples to define jargon.
    """
    with st.expander("ℹ️ How this page works", expanded=expanded):
        st.markdown(what)
        if steps:
            st.markdown("**What to do here**")
            st.markdown("\n".join(f"{i+1}. {s}" for i, s in enumerate(steps)))
        if terms:
            st.markdown("**Key terms**")
            st.markdown("\n".join(f"- **{t}** — {d}" for t, d in terms))


def _resource_bar(team):
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Capital", f"${team['capital']:,.0f}",
              help="Simulated cash. Spent on experiments and pivots. Runs out if you "
                   "over-invest, so test the cheapest way first.")
    c2.metric("Evidence Credits", f"{team['evidence_credits']:,.1f}",
              help="The simulation's main currency. You EARN credits by logging credible "
                   "evidence and SPEND them on experiments, specialists, and pivots.")
    c3.metric("Founder-hours", f"{team['founder_hours']:,.0f}",
              help="Your team's available time. Every experiment consumes hours as well "
                   "as money.")
    c4.metric("Venture Tokens", f"{team['venture_tokens']}",
              help="Used only in the Value Proposition Auction to reveal which idea you "
                   "back most confidently.")


def _refresh_team(team_id):
    return db.get_team(team_id)


def _shade_row(label, done, must_update):
    """One shaded checklist row (green = done, amber = required-incomplete)."""
    if done:
        bg, border, icon = "#e7f4ea", "#34a853", "✅"
    else:
        bg, border, icon = "#fdf1d6", "#f5a623", "⬜"
    tag = " <span style='color:#b26a00;font-weight:600;'>· must complete this round</span>" \
        if (must_update and not done) else ""
    return ("<div style='background:%s;border-left:4px solid %s;padding:6px 10px;"
            "margin:4px 0;border-radius:4px;'>%s %s%s</div>" % (bg, border, icon, label, tag))


def _render_checklist(items):
    """Render a shaded checklist from [{label, done, must_update}] as one HTML block."""
    html = "".join(_shade_row(i["label"], i["done"], i.get("must_update", False)) for i in items)
    st.markdown(html, unsafe_allow_html=True)


def _page_requirements(page, team):
    """Shaded 'required this round' box for the requirements tied to this page."""
    rnd = db.current_round()
    prog = [p for p in logic.round_progress(team["id"], rnd) if p.get("tool") == page]
    if prog:
        st.markdown("**✅ Required on this page this round**")
        _render_checklist(prog)


def _round_gate(page, team):
    """Enforce round alignment on a tool page.

    Returns (editable: bool). Locked tools show a lock screen and stop; reference
    tools (introduced but not relevant this round, strict mode) become view-only.
    Also shades this page's required deliverables when active.
    """
    rnd = db.current_round()
    state = logic.tool_state(page, rnd)
    if state == "locked":
        wk = logic.page_unlock_round(page)
        st.warning(f"🔒 **Locked.** This tool is introduced in **Round {wk}**. "
                   f"You're in Round {rnd}. It will open when its concepts are taught.")
        st.stop()
    editable = logic.tool_editable(page, rnd)
    if state == "reference" and not editable:
        st.info("👁️ **Reference only this round.** This tool isn't part of the current round's "
                "task, so editing is disabled to keep everyone focused. Your existing work is "
                "shown below and carries forward. (Your instructor can re-enable edits by "
                "turning off Strict round mode.)")
    elif state == "active":
        _page_requirements(page, team)
    return editable


def _ai_check_notice():
    """Reusable reminder wherever generative AI is likely to be used."""
    with st.expander("🤖 Using generative AI here? Run the AUDIT check first"):
        st.markdown(content.AI_PROTOCOL_SUMMARY)


# --------------------------------------------------------------------------- #
# Round Briefing — the week's learning objectives and simulation task
# --------------------------------------------------------------------------- #
def round_briefing(team):
    cur = db.current_round()
    topics = logic.topics_for_round(cur)
    titles = " + ".join(t["title"] for t in topics) if topics else ""
    st.subheader(f"📅 Round Briefing — Round {cur}" + (f": {titles}" if titles else ""))
    _guide(
        "The simulation adds complexity round by round. In the first class session your "
        "instructor introduces new concepts; the simulation round is where you apply them. "
        "A single round may cover several pieces of material (your instructor decides how the "
        "curriculum is packed into the number of rounds). Start here every round: it lists the "
        "learning objectives, what's new, the tasks, and which tools to use. You'll also use "
        "generative AI — remember to verify what it produces (see the AI reminder below).",
        terms=[
            ("Learning objectives", "What you should be able to DO by the end of this round."),
            ("Concepts introduced", "New ideas taught in class this round."),
            ("This round's tasks", "The specific simulation actions to complete now."),
        ],
    )
    if not topics:
        st.info("No material is assigned to this round yet — check with your instructor.")
        return

    for i, tp in enumerate(topics):
        if i:
            st.divider()
        st.write(f"### 🎓 {tp['title']}")
        st.caption(f"In class: {tp['class_focus']}")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Learning objectives**")
            for o in tp["objectives"]:
                st.markdown(f"- {o}")
        with c2:
            st.markdown("**Concepts introduced**")
            for c in tp["concepts"]:
                st.markdown(f"- {c}")
        st.success(f"**🎯 Task:** {tp['sim_task']}  ·  **Go to:** *{tp['tool']}*")

    # ---- Completion checklist (shaded) --------------------------------------
    st.divider()
    prog = logic.round_progress(team["id"], cur)
    done_n = sum(1 for p in prog if p["done"])
    complete = done_n == len(prog)
    st.write(f"### ✅ To finish Round {cur} — {done_n}/{len(prog)} complete")
    if complete:
        st.success("All required deliverables are complete for this round. 🎉")
    else:
        st.caption("Amber items must be completed this round. Green items are done.")
    _render_checklist(prog)

    # ---- What must change vs. what can remain -------------------------------
    tool_pages = ["Founder & Opportunity", "Canvases", "VP Auction", "Assumption Map",
                  "Experiment Marketplace", "Evidence Ledger", "Market Events",
                  "Pivot Petition"]
    reference = [p for p in tool_pages if logic.tool_state(p, cur) == "reference"]
    locked = [p for p in tool_pages if logic.tool_state(p, cur) == "locked"]
    must_change = sorted({p["tool"] for p in prog if p.get("must_update") and not p["done"]})
    cc1, cc2 = st.columns(2)
    with cc1:
        st.markdown("**✍️ Must change this round**")
        if must_change:
            for t in must_change:
                st.markdown(f"- {t}")
        else:
            st.caption("Nothing outstanding — you're up to date.")
    with cc2:
        st.markdown("**📌 Can remain (carried forward)**")
        if reference:
            for t in reference:
                st.markdown(f"- {t} — no change needed unless new evidence says so")
        else:
            st.caption("—")
    if locked:
        st.caption("🔒 Not yet available: " + ", ".join(locked))

    # What unlocks this round (excluding base tools already available)
    newly = [p for p in logic.newly_unlocked(cur) if p not in content.BASE_TOOLS]
    if newly:
        st.info("🔓 **New this round:** " + ", ".join(newly))

    st.divider()
    st.markdown("**🤖 Generative AI this round**")
    st.markdown(content.AI_PROTOCOL_SUMMARY)

    with st.expander(f"Full {logic.total_rounds()}-round plan (how complexity builds)"):
        st.dataframe(
            [{"Round": row["round"],
              "Material": " + ".join(t["title"] for t in row["topics"]) or "—",
              "Tasks": " / ".join(t["sim_task"] for t in row["topics"])}
             for row in logic.get_schedule()],
            use_container_width=True, hide_index=True,
        )


# --------------------------------------------------------------------------- #
# Inbox — in-app feedback "email" from the Director / Auto-Director
# --------------------------------------------------------------------------- #
def inbox(team):
    st.subheader("📬 Inbox")
    _guide(
        "After each round you receive a venture review here — an in-app email from the Foundry "
        "summarizing your predicted performance, what's working, where to focus, your untested "
        "risks, and a recommended next step. New messages are marked unread; open one to read "
        "the full review.",
        terms=[
            ("Venture review", "Your per-round feedback email."),
            ("Unread", "A message you haven't opened yet (shown with 🔵)."),
        ],
    )
    msgs = db.list_messages(team["id"])
    top = st.columns([3, 1])
    top[0].caption(f"{len(msgs)} message(s) · {db.unread_count(team['id'])} unread")
    if msgs and top[1].button("Mark all read"):
        db.mark_all_read(team["id"])
        st.rerun()

    if not msgs:
        st.info("No messages yet. Your first venture review arrives after this round is scored.")
        return

    for m in msgs:
        dot = "🔵 " if not m["read"] else ""
        with st.expander(f"{dot}{m['subject']} · {m['created_at']}"):
            st.caption(f"From: {m['sender']}" + (f" · Round {m['round']}" if m["round"] else ""))
            st.text(m["body"])
            cols = st.columns(2)
            if not m["read"] and cols[0].button("Mark read", key=f"msgread_{m['id']}"):
                db.mark_message_read(m["id"])
                st.rerun()
            if cols[1].button("Delete", key=f"msgdel_{m['id']}"):
                db.delete_message(m["id"])
                st.rerun()


# --------------------------------------------------------------------------- #
# Dashboard
# --------------------------------------------------------------------------- #
def dashboard(team):
    st.subheader(f"🏭 {team['name']} — Venture Dashboard")
    st.caption(f"Stage: **{team['stage']}**  ·  Round {db.current_round()}  ·  "
               f"Join code `{team['join_code']}`")
    _guide(
        "This is your venture's home screen. It shows what you own (top row), what your "
        "venture is worth, how the Director has scored you, and where your biggest risks "
        "are. You don't enter anything here — it summarizes everything you do on the other "
        "pages. Check it at the start and end of every round.",
        terms=[
            ("Venture Valuation", "A simulated score, not a real dollar figure. It rewards "
             "evidence and coherence, not a flashy idea."),
            ("Performance dimensions", "Ten qualities the Director grades 0–100 each round."),
            ("High-risk untested", "Important assumptions you have not backed with evidence — "
             "the fastest way to lose the game is to ignore these."),
        ],
    )
    _resource_bar(team)

    val = logic.compute_valuation(team["id"])
    st.divider()
    vc1, vc2 = st.columns([1, 2])
    with vc1:
        st.metric("Venture Valuation", f"${val['valuation']:,.0f}",
                  help="Market Potential × Evidence Confidence × Business-Model Coherence × "
                       "Execution − Unresolved Risk. Raising evidence and coherence raises "
                       "this number.")
        st.caption("Potential × Evidence × Coherence × Execution − Risk")
    with vc2:
        st.write("**Valuation components** — each multiplier runs from ×0.50 (weak) to "
                 "×1.50 (strong) and comes from the Director's dashboard scores:")
        st.write(
            f"- Market potential: ${val['market_potential']:,.0f}\n"
            f"- Evidence confidence: ×{val['evidence_confidence']}\n"
            f"- Business-model coherence: ×{val['bm_coherence']}\n"
            f"- Execution factor: ×{val['execution_factor']}\n"
            f"- Unresolved-risk penalty: −${val['unresolved_risk']:,.0f}"
        )

    st.divider()
    st.write("### Performance dimensions")
    st.caption("Set by the Director each round (0–100). Empty bars just mean 'not scored yet.'")
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
    st.write("### Risk snapshot")
    esum = logic.evidence_summary(team["id"])
    arep = logic.assumption_risk_report(team["id"])
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Evidence items", esum["count"],
              help="How many pieces of evidence you've logged on the Evidence Ledger page.")
    m2.metric("Behavioral evidence", esum["behavioral"],
              help="Evidence based on what customers actually DID (strength 6+). Worth far "
                   "more than opinions.")
    m3.metric("Assumptions untested", arep["untested"],
              help="Beliefs you have not yet tested on the Assumption Map page.")
    m4.metric("High-risk untested", len(arep["exposed"]),
              help="Important assumptions with no evidence. Test these first.")
    if arep["exposed"]:
        st.warning(
            "⚠️ High-importance assumptions with no evidence — these can invalidate the "
            "venture if they fail:\n\n"
            + "\n".join(f"- {a['text']} ({a['risk_type']})" for a in arep["exposed"])
        )

    with st.expander("Transaction ledger — every time you gained or spent resources"):
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
    editable = _round_gate("Founder & Opportunity", team)
    _guide(
        "You are founders newly accepted into the Venture Foundry accelerator. You do NOT "
        "start with a product — you start with a broad **opportunity territory** and a "
        "**founder card** listing your team's skills, money, and time. Your first job is to "
        "invent at least three possible ventures inside that territory and score each one, "
        "so you commit deliberately instead of falling in love with the first idea.",
        steps=[
            "Read your founder card and opportunity territory below.",
            "Add three or more candidate ventures using the form.",
            "Score each on the five sliders (1 = poor, 5 = excellent).",
            "Compare them and discuss which to pursue — higher total scores are stronger bets.",
        ],
        terms=[
            ("Opportunity territory", "A problem area (e.g. 'reducing food waste'), not a "
             "product. Many ventures could live inside it."),
            ("Founder card", "Your fixed constraints for the semester: skills, network, "
             "budget you can afford to lose, and hours available."),
            ("Founder–opportunity fit", "How well your specific skills and network match "
             "what this venture would need."),
        ],
    )

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
            if st.button("Remove", key=f"rmv_{i}", disabled=not editable,
                         help="Delete this candidate venture."):
                ventures.pop(i)
                db.set_ventures(team["id"], ventures)
                st.rerun()

    with st.form("add_venture", clear_on_submit=True):
        st.write("**Add a candidate venture**")
        name = st.text_input(
            "Venture name / one-line description",
            help="A short pitch of one possible business inside your territory, e.g. "
                 "'App that resells near-expiry grocery items to students.'")
        c1, c2, c3 = st.columns(3)
        importance = c1.slider(
            "Customer importance", 1, 5, 3,
            help="How badly does the customer need this solved? 1 = nice-to-have, "
                 "5 = urgent, painful problem.")
        fit = c2.slider(
            "Founder–opportunity fit", 1, 5, 3,
            help="How well do YOUR skills and network match this venture? 5 = perfect fit.")
        access = c3.slider(
            "Access to customers", 1, 5, 3,
            help="Can you actually reach these customers to interview and sell? "
                 "5 = easy access.")
        c4, c5 = st.columns(2)
        evidence = c4.slider(
            "Evidence availability", 1, 5, 3,
            help="How easily could you gather real evidence about this idea? "
                 "5 = evidence is easy to collect.")
        afford = c5.slider(
            "Experiment affordability", 1, 5, 3,
            help="Can you test this cheaply with your money and hours? "
                 "5 = very cheap to test.")
        notes = st.text_area(
            "Notes",
            help="Anything else worth remembering about this option — risks, ideas, "
                 "who to talk to.")
        if st.form_submit_button("Add venture", disabled=not editable,
                                 help="Save this candidate venture to your list.") and name:
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

_CANVAS_HELP = {
    "customer_profile": "Describes ONE customer segment: the jobs they're trying to get "
                        "done, the pains they suffer, and the gains they want. Fill this in "
                        "from real interviews, not guesses.",
    "vpc": "The Value Proposition Canvas maps how your offer relieves specific pains and "
           "creates specific gains for that customer. A good value proposition 'fits' the "
           "customer profile.",
    "bmc": "The Business Model Canvas describes the whole business on nine blocks — who you "
           "serve, what you offer, how you reach and keep them, how you make money, and what "
           "it costs. The nine blocks depend on each other, so a change in one affects others.",
}


def _cbox(parent, title, key, prefill, height=120, hint=""):
    """Render one canvas block (bordered box, title, textarea) and return its value.

    `parent` may be the `st` module or a column — both expose .container()/.text_area(),
    so we call methods directly rather than using a `with` block (the module isn't a
    context manager).
    """
    box = parent.container(border=True)
    box.markdown(f"**{title}**")
    if hint:
        box.caption(hint)
    return box.text_area(title, value=prefill, key=key, height=height,
                         label_visibility="collapsed")


def _customer_profile_layout(ctype, val):
    """Strategyzer Customer Profile (the circle): Gains, Jobs, Pains."""
    st.caption("The customer 'circle' — describe the segment from the outside in. "
               "Gains (wanted outcomes) · Jobs (what they're trying to get done) · Pains (bad outcomes).")
    data = {}
    data["gains"] = _cbox(st, "😀 Gains (top of circle)", f"{ctype}_gains", val("gains"),
                          110, "Benefits and positive outcomes the customer wants.")
    data["customer_jobs"] = _cbox(st, "🎯 Customer Jobs (centre)", f"{ctype}_customer_jobs",
                                  val("customer_jobs"), 110,
                                  "Functional, social, and emotional jobs they're trying to get done.")
    data["pains"] = _cbox(st, "😣 Pains (bottom of circle)", f"{ctype}_pains", val("pains"),
                          110, "Frustrations, risks, and obstacles they experience.")
    return data


def _vpc_layout(ctype, val):
    """Value Proposition Canvas: value map (square, left) + customer profile (circle, right)."""
    st.caption("Left = **Value Map** (the square, your offer). Right = **Customer Profile** "
               "(the circle, the customer). A good value proposition 'fits': gain creators → "
               "gains, pain relievers → pains, products & services → jobs.")
    left, right = st.columns(2)
    data = {}
    left.markdown("#### ▮ Value Map")
    data["gain_creators"] = _cbox(left, "➕ Gain Creators (top)", f"{ctype}_gain_creators",
                                  val("gain_creators"), 100,
                                  "How your offer produces the gains customers want.")
    data["products_services"] = _cbox(left, "📦 Products & Services (centre)",
                                      f"{ctype}_products_services", val("products_services"),
                                      100, "What you offer that addresses the customer's jobs.")
    data["pain_relievers"] = _cbox(left, "🩹 Pain Relievers (bottom)", f"{ctype}_pain_relievers",
                                   val("pain_relievers"), 100,
                                   "How your offer eases specific customer pains.")
    right.markdown("#### ◯ Customer Profile")
    data["gains_created"] = _cbox(right, "😀 Gains (top)", f"{ctype}_gains_created",
                                  val("gains_created"), 100, "The specific gains you create.")
    data["jobs_addressed"] = _cbox(right, "🎯 Customer Jobs (centre)", f"{ctype}_jobs_addressed",
                                   val("jobs_addressed"), 100, "The jobs this proposition targets.")
    data["pains_reduced"] = _cbox(right, "😣 Pains (bottom)", f"{ctype}_pains_reduced",
                                  val("pains_reduced"), 100, "The specific pains you reduce.")
    return data


def _bmc_layout(ctype, val):
    """Business Model Canvas in its canonical nine-block grid."""
    st.caption("The nine blocks in their standard Strategyzer positions. Infrastructure on the "
               "left, customers on the right, value in the centre, finances along the bottom. "
               "Remember: the blocks depend on each other.")
    data = {}
    top = st.columns(5)
    data["key_partners"] = _cbox(top[0], "🤝 Key Partners", f"{ctype}_key_partners",
                                 val("key_partners"), 240, "Who helps you?")
    data["key_activities"] = _cbox(top[1], "⚙️ Key Activities", f"{ctype}_key_activities",
                                   val("key_activities"), 100, "What you must do well.")
    data["key_resources"] = _cbox(top[1], "🏭 Key Resources", f"{ctype}_key_resources",
                                  val("key_resources"), 100, "Assets the model requires.")
    data["value_propositions"] = _cbox(top[2], "💡 Value Propositions", f"{ctype}_value_propositions",
                                       val("value_propositions"), 240, "The value you deliver.")
    data["customer_relationships"] = _cbox(top[3], "❤️ Customer Relationships",
                                           f"{ctype}_customer_relationships",
                                           val("customer_relationships"), 100,
                                           "The relationship each segment expects.")
    data["channels"] = _cbox(top[3], "🚚 Channels", f"{ctype}_channels", val("channels"),
                             100, "How you reach and deliver to customers.")
    data["customer_segments"] = _cbox(top[4], "👥 Customer Segments", f"{ctype}_customer_segments",
                                      val("customer_segments"), 240, "For whom you create value.")
    bottom = st.columns(2)
    data["cost_structure"] = _cbox(bottom[0], "💸 Cost Structure", f"{ctype}_cost_structure",
                                   val("cost_structure"), 100, "The dominant costs.")
    data["revenue_streams"] = _cbox(bottom[1], "💰 Revenue Streams", f"{ctype}_revenue_streams",
                                    val("revenue_streams"), 100, "How you earn revenue.")
    return data


def canvases(team):
    st.subheader("🗂️ Canvases")
    editable = _round_gate("Canvases", team)
    cur = db.current_round()
    cp_wk = logic.canvas_unlock_round("customer_profile")
    vpc_wk = logic.canvas_unlock_round("vpc")
    bmc_wk = logic.canvas_unlock_round("bmc")
    _guide(
        "These are the real Strategyzer canvases, laid out as they appear on paper. Treat every "
        "box as a **hypothesis** you'll later test, not a fact. Each time you learn something, "
        "save a NEW version with a note on what changed — the simulation grades how your "
        "thinking evolves. The three canvases are staged so no single round is overloaded: "
        f"Customer Profile from Round {cp_wk}, the Value Proposition Canvas from Round {vpc_wk}, "
        f"and the Business Model Canvas from Round {bmc_wk}.",
        steps=[
            "Work on the canvas that's in focus this round (shown below).",
            "Fill the boxes in their canonical positions. Empty is fine early on.",
            "Add a short 'what changed / why' note, then Save to create a dated version.",
            "Return after experiments and save new versions as evidence comes in.",
        ],
        terms=[
            ("Customer Profile", "The circle: jobs, pains, and gains of one segment."),
            ("Value Proposition Canvas", "Value map (square) + customer profile (circle) — the 'fit'."),
            ("Business Model Canvas", "The nine blocks of the whole business."),
            ("Version", "A dated snapshot. Saving again makes v2, v3… so learning is visible."),
        ],
    )
    _ai_check_notice()

    focuses = logic.canvas_focus_for_round(cur)   # list (a round may cover several)
    focus_names = [_CANVAS_DEFS[f][0] for f in focuses if f in _CANVAS_DEFS]
    if focus_names:
        st.info("🎯 **This round's canvas focus:** " + ", ".join(focus_names))

    canvas_keys = list(_CANVAS_DEFS.keys())
    default_idx = canvas_keys.index(focuses[0]) if focuses and focuses[0] in canvas_keys else 0
    ctype = st.selectbox(
        "Canvas type", canvas_keys, index=default_idx,
        format_func=lambda k: _CANVAS_DEFS[k][0],
        help="Customer Profile → Value Proposition Canvas → Business Model Canvas is the "
             "guided order; each is introduced a few rounds apart.",
    )
    title, blocks = _CANVAS_DEFS[ctype]
    unlock = logic.canvas_unlock_round(ctype)
    if cur < unlock:
        st.warning(f"🔒 The {title} is introduced in **Round {unlock}**. You can sketch it "
                   "early, but its concepts are taught then.")
    st.caption(_CANVAS_HELP[ctype])

    existing = db.list_canvases(team["id"], ctype)
    latest = existing[-1] if existing else None

    def val(key):
        return latest["data"].get(key, "") if latest else ""

    st.write(f"### {title}")
    if existing:
        st.caption(f"{len(existing)} version(s) saved. Editing starts from the latest.")

    with st.form(f"canvas_{ctype}", clear_on_submit=False):
        if ctype == "customer_profile":
            data = _customer_profile_layout(ctype, val)
        elif ctype == "vpc":
            data = _vpc_layout(ctype, val)
        else:
            data = _bmc_layout(ctype, val)

        st.divider()
        vlabel = st.text_input(
            "Version label (optional)", value=f"{title} v{len(existing)+1}",
            help="A name for this snapshot, e.g. 'after 5 interviews'. Auto-filled for you.")
        note = st.text_input(
            "What changed / why (evidence-driven?)",
            help="One line on what you changed and what evidence prompted it. This is graded — "
                 "it shows your thinking evolved for a reason.")
        if st.form_submit_button(f"Save new {title} version", disabled=not editable,
                                 help="Store the current boxes as a new dated version."):
            v = db.save_canvas(team["id"], ctype, data, vlabel, note)
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
    editable = _round_gate("Assumption Map", team)
    _guide(
        "Every box on your canvases hides an assumption — something that must be TRUE for the "
        "venture to work. Here you list those assumptions and rank them. The simulation "
        "penalizes you if an assumption you called important turns out false and you never "
        "tested it, so this page tells you what to test next.",
        steps=[
            "Write each assumption as a statement that must be true (see the example).",
            "Pick its risk type and set the three sliders.",
            "Add it. The list auto-sorts by priority (important + little evidence = top).",
            "Take the top assumptions to the Experiment Marketplace to test them.",
            "Update an assumption's status as you learn (Supported / Refuted).",
        ],
        terms=[
            ("Desirability", "Do customers actually want it?"),
            ("Feasibility", "Can we build and deliver it?"),
            ("Viability", "Can we make money — will they pay, do the costs work?"),
            ("Adaptability", "Will it survive competitors, rules, and change?"),
            ("Priority", "Importance × how little evidence you have. High = test this first."),
        ],
    )

    with st.form("add_assumption", clear_on_submit=True):
        text = st.text_input(
            "Assumption (state it as something that must be true)",
            placeholder="Customers will pay at least $20/month for this.",
            help="Phrase it as a testable claim. Good: 'Coffee shops will pay $49/mo.' "
                 "Bad: 'Pricing.'")
        c1, c2, c3, c4 = st.columns(4)
        risk = c1.selectbox(
            "Risk type", content.RISK_TYPES,
            help="Which kind of risk is this? Desirability = do they want it; Feasibility = "
                 "can we build it; Viability = does the money work; Adaptability = will it last.")
        importance = c2.slider(
            "Importance", 1, 5, 3,
            help="If this assumption is FALSE, how badly is the venture hurt? "
                 "5 = the whole venture collapses.")
        evidence_level = c3.slider(
            "Existing evidence", 1, 5, 1,
            help="How much solid evidence do you already have for this? "
                 "1 = only a hunch, 5 = strong proof.")
        testability = c4.slider(
            "Testability", 1, 5, 3,
            help="How easily can you test this cheaply and quickly? 5 = very easy to test.")
        if st.form_submit_button("Add assumption", disabled=not editable,
                                 help="Save this assumption to your map.") and text:
            db.add_assumption(team["id"], text, risk, importance, evidence_level, testability)
            st.success("Assumption added.")
            st.rerun()

    assums = db.list_assumptions(team["id"])
    if not assums:
        st.info("No assumptions yet. Add the beliefs your venture depends on using the form above.")
        return

    st.divider()
    st.write("### Prioritization — importance vs. evidence")
    st.caption("Sorted so the riskiest untested beliefs are at the top. "
               "Priority = importance × (6 − existing evidence).")
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
                help="Untested = no evidence yet; Testing = experiment running; "
                     "Supported/Refuted = evidence came back; Ignored = you chose not to test "
                     "(risky if it's important).",
            )
            cc1, cc2 = st.columns(2)
            if cc1.button("Update status", key=f"aupd_{a['id']}", disabled=not editable,
                          help="Save the status you selected."):
                db.update_assumption(a["id"], status=new_status)
                st.rerun()
            if cc2.button("Delete", key=f"adel_{a['id']}", disabled=not editable,
                          help="Remove this assumption."):
                db.delete_assumption(a["id"])
                st.rerun()


# --------------------------------------------------------------------------- #
# Experiment marketplace
# --------------------------------------------------------------------------- #
def experiments(team):
    st.subheader("🧪 Experiment Marketplace")
    editable = _round_gate("Experiment Marketplace", team)
    _guide(
        "This is where you buy tests for your assumptions. Each experiment card costs money, "
        "hours, and Evidence Credits, and gives evidence of a certain strength. The key "
        "discipline: you must write down what result would count as success or failure BEFORE "
        "you run it, so you can't move the goalposts afterward.",
        steps=[
            "Pick an experiment card and read its cost, strength, and best-fit risk type.",
            "Choose which assumption it tests.",
            "Write a hypothesis, a metric, and success + failure thresholds.",
            "Write your decision rule (what you'll do for each outcome).",
            "Purchase & design it — resources are deducted and the assumption is marked 'Testing.'",
            "Run the test in the real world, then record the result and outcome below.",
        ],
        terms=[
            ("Evidence strength", "How convincing this test is, 0–10. Behavior beats opinions."),
            ("Metric", "The single number you'll measure, e.g. '# who request a trial.'"),
            ("Threshold", "The line that defines success vs. failure, set in advance."),
            ("Decision rule", "What you'll DO for each outcome — persevere, pivot, or stop."),
        ],
    )
    team = _refresh_team(team["id"])
    _resource_bar(team)

    assums = db.list_assumptions(team["id"])
    if not assums:
        st.warning("Add assumptions first on the **Assumption Map** page — every experiment "
                   "must test a specific assumption.")
    st.divider()

    st.write("### Buy & design an experiment")
    card_name = st.selectbox(
        "Experiment card", [c["name"] for c in content.EXPERIMENT_CARDS],
        help="Each card is a different way to test a belief. Cheaper cards give weaker "
             "evidence; behavior-based cards (preorder, letter of intent) give the strongest.")
    card = content.EXPERIMENT_CARD_MAP[card_name]
    ic1, ic2, ic3, ic4 = st.columns(4)
    ic1.metric("Money", f"${card['money']}", help="Capital this experiment costs.")
    ic2.metric("Hours", f"{card['hours']}", help="Founder-hours this experiment consumes.")
    ic3.metric("Credits", f"{card['credits']}", help="Evidence Credits this experiment costs.")
    ic4.metric("Evidence strength", f"{card['strength']}/10",
               help="How strong the resulting evidence is if the test is done well.")
    st.caption(f"Best for **{card['suits']}** assumptions · Min sample: {card['sample']} · "
               f"Watch for bias: {card['bias']}")

    with st.form("buy_experiment", clear_on_submit=True):
        if assums:
            assum_id = st.selectbox(
                "Assumption tested",
                [a["id"] for a in assums],
                format_func=lambda i: next(a["text"] for a in assums if a["id"] == i),
                help="Which belief will this experiment test? Pick the riskiest untested one.")
        else:
            assum_id = None
        hypothesis = st.text_area(
            "Hypothesis",
            placeholder="We believe independent coffee shops will pay $49/mo for automated inventory forecasting.",
            help="Your specific, falsifiable prediction. Start with 'We believe…' and include "
                 "who, what, and how much.")
        metric = st.text_input(
            "Metric", placeholder="Number of shop owners requesting a trial",
            help="The one number you'll measure to judge the hypothesis.")
        c1, c2 = st.columns(2)
        success = c1.text_input(
            "Success threshold", placeholder="≥5 request a trial and ≥2 share sales data",
            help="The result that would make you believe the assumption. Set it BEFORE testing.")
        failure = c2.text_input(
            "Failure threshold", placeholder="≤1 requests a trial",
            help="The result that would make you reject the assumption. Set it BEFORE testing.")
        decision = st.text_input(
            "Decision rule",
            placeholder="If supported, build clickable prototype; if refuted, revisit segment",
            help="What you will actually DO depending on the outcome.")
        submitted = st.form_submit_button(
            "Purchase & design experiment", disabled=not editable,
            help="Deducts the cost and saves the experiment. The assumption becomes 'Testing.'")
        if submitted:
            if assum_id is None:
                st.error("Add an assumption to test first (Assumption Map page).")
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
    st.caption("Run each test in the real world, then come back and record what happened.")
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
            result = st.text_area(
                "Record result", value=e["result"] or "", key=f"res_{e['id']}",
                help="What actually happened? Enter the measured numbers and what you observed.")
            outcome = st.selectbox(
                "Outcome", ["Designed", "Running", "Supported", "Refuted", "Inconclusive"],
                index=["Designed", "Running", "Supported", "Refuted", "Inconclusive"].index(e["outcome"]),
                key=f"outc_{e['id']}",
                help="Compare the result to your thresholds. Supported/Refuted will auto-update "
                     "the linked assumption. Inconclusive = the test didn't settle it.")
            if st.button("Save result", key=f"saveres_{e['id']}", disabled=not editable,
                         help="Store the result and update the linked assumption."):
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
    editable = _round_gate("Evidence Ledger", team)
    _guide(
        "This is your proof file and your income source. Every time you gather real evidence, "
        "log it here. The simulation pays you Evidence Credits equal to the evidence's strength "
        "on the ladder below — so a signed letter of intent (9) is worth far more than a "
        "friend saying 'cool idea' (1). Behavior beats opinion.",
        steps=[
            "Open the ladder below to see how evidence is valued.",
            "Describe what you learned in one line.",
            "Pick the evidence type that matches HOW you learned it.",
            "Add the source and optionally link it to an assumption.",
            "Log it — you're paid credits automatically based on strength.",
        ],
        terms=[
            ("Behavioral evidence", "Based on what customers DID (bought, signed, tried). "
             "Strength 6+."),
            ("Opinion evidence", "Based on what people SAID they might do. Strength 0–2, "
             "easy to get but weak."),
            ("Evidence Credits", "Currency you earn here and spend on experiments and pivots."),
        ],
    )

    with st.expander("📊 Evidence-strength ladder — how each type is valued"):
        st.table([{"Evidence": lbl, "Value (0–10)": val} for lbl, val in content.EVIDENCE_LADDER])

    assums = db.list_assumptions(team["id"])
    with st.form("add_evidence", clear_on_submit=True):
        description = st.text_input(
            "What did you learn? (one line)",
            placeholder="3 of 5 shop owners asked to join a paid pilot.",
            help="A short factual summary of the evidence, not your interpretation.")
        etype = st.selectbox(
            "Evidence type", [lbl for lbl, _ in content.EVIDENCE_LADDER],
            help="Choose based on HOW you learned it. Higher on the list = stronger = more "
                 "credits. Be honest: a hallway 'sounds good' is an opinion, not behavior.")
        source = st.text_input(
            "Source", placeholder="e.g., Interview with 3 coffee-shop owners",
            help="Where the evidence came from — who, how many, and when.")
        if assums:
            assum_id = st.selectbox(
                "Related assumption (optional)",
                [None] + [a["id"] for a in assums],
                format_func=lambda i: "—" if i is None else next(a["text"] for a in assums if a["id"] == i),
                help="Link this evidence to the assumption it supports or challenges.")
        else:
            assum_id = None
        if st.form_submit_button(
                "Log evidence", disabled=not editable,
                help="Records the evidence and pays you credits equal to its strength.") and description:
            award, strength = logic.log_evidence_and_award(
                team["id"], description, etype, source, assum_id)
            st.success(f"Logged. Strength {strength}/10 → earned {award} Evidence Credits.")
            st.rerun()

    st.divider()
    esum = logic.evidence_summary(team["id"])
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Items", esum["count"], help="Total pieces of evidence logged.")
    c2.metric("Avg strength", esum["avg_strength"],
              help="Average strength of your evidence. Aim to raise this over time.")
    c3.metric("Behavioral", esum["behavioral"], help="Evidence of strength 6+ (what people did).")
    c4.metric("Opinion-only", esum["opinion"], help="Weak evidence of strength ≤2 (what people said).")

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
    editable = _round_gate("VP Auction", team)
    _guide(
        f"You created several value propositions — now show which you back most. You have "
        f"{content.VENTURE_TOKEN_POOL} Venture Tokens to spread across them. Betting big on an "
        "idea your evidence doesn't support costs you credits (an Overconfidence Tax). Moving "
        "your tokens toward better-supported ideas after you learn earns you credits (a Learning "
        "Dividend). This rewards changing your mind when the evidence says so.",
        steps=[
            f"Create at least {content.MIN_VALUE_PROPS} value propositions (form below).",
            "Set each one's evidence support (0–10) to match what your Evidence Ledger shows.",
            f"Allocate your {content.VENTURE_TOKEN_POOL} tokens across them.",
            "Watch the live preview: aim for high Alignment, low Tax.",
            "Submit. Net credits (dividend − tax) are applied and the round is recorded.",
        ],
        terms=[
            ("Value proposition", "One specific way you create value for the customer segment."),
            ("Evidence support", "How well real evidence backs this proposition, 0–10."),
            ("Alignment", "Your tokens weighted by evidence support. High = you're backing "
             "what the evidence supports."),
            ("Overconfidence Tax", "Credit penalty for putting tokens on weakly-supported ideas."),
            ("Learning Dividend", "Credit reward for shifting tokens toward evidence vs. last time."),
        ],
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
            new_ev = st.slider(
                "Evidence support", 0, 10, int(p["evidence_strength"]),
                key=f"vpev_{p['id']}",
                help="How strongly does real evidence back this proposition? 0 = pure hope, "
                     "10 = customers are paying. Be honest — the Director can override it.")
            c1, c2 = st.columns(2)
            if c1.button("Update evidence", key=f"vpupd_{p['id']}", disabled=not editable,
                         help="Save the evidence-support level you set."):
                db.update_value_prop(p["id"], evidence_strength=new_ev)
                st.rerun()
            if c2.button("Delete", key=f"vpdel_{p['id']}", disabled=not editable,
                         help="Remove this proposition."):
                db.delete_value_prop(p["id"])
                st.rerun()

    with st.form("add_vp", clear_on_submit=True):
        st.write("**Add a value proposition**")
        name = st.text_input(
            "Name", help="A short label for this proposition, e.g. 'Subscription forecasting.'")
        desc = st.text_area(
            "Products/services · pain relievers · gain creators",
            help="Describe what you offer and how it eases the customer's pains and creates "
                 "gains.")
        ev = st.slider(
            "Evidence support (0–10)", 0, 10, 0,
            help="Start at 0 if untested. Raise it only as real evidence comes in.")
        if st.form_submit_button("Add proposition", disabled=not editable,
                                 help="Save this proposition to the auction.") and name:
            db.add_value_prop(team["id"], name, desc, ev)
            st.rerun()

    if len(props) < content.MIN_VALUE_PROPS:
        st.warning(f"Add at least {content.MIN_VALUE_PROPS} propositions to run the auction "
                   f"(you have {len(props)}). Competing options stop you from locking onto the "
                   "first idea.")
        return

    # ---- Allocate tokens -----------------------------------------------------
    st.divider()
    st.write(f"### Allocate {content.VENTURE_TOKEN_POOL} Venture Tokens")
    st.caption("Put more tokens on the propositions you're most confident in. The preview "
               "updates as you type.")
    allocations = {}
    cols = st.columns(min(len(props), 4))
    for i, p in enumerate(props):
        with cols[i % len(cols)]:
            allocations[p["id"]] = st.number_input(
                p["name"], min_value=0, max_value=content.VENTURE_TOKEN_POOL,
                value=int(p["tokens"]), step=5, key=f"vptok_{p['id']}",
                help=f"Tokens on '{p['name']}' (evidence {p['evidence_strength']}/10). "
                     "All allocations must sum to no more than the pool.")
    total = sum(allocations.values())
    remaining = content.VENTURE_TOKEN_POOL - total
    (st.error if remaining < 0 else st.caption)(
        f"Allocated {total} / {content.VENTURE_TOKEN_POOL} · {remaining} remaining")

    preview = logic.preview_vp_auction(team["id"], allocations)
    if preview.get("ok"):
        pc1, pc2, pc3, pc4 = st.columns(4)
        pc1.metric("Alignment", preview["alignment"],
                   help="0–1. Your tokens weighted by evidence support. Higher is better.")
        pc2.metric("Overconfidence Tax", f"-{preview['tax']}",
                   help="Credits you'll lose for backing weakly-supported propositions.")
        pc3.metric("Learning Dividend", f"+{preview['dividend']}",
                   help="Credits you'll gain for shifting toward evidence vs. your last auction.")
        pc4.metric("Net credits", preview["net"],
                   help="Dividend minus tax. This is applied when you submit.")
        st.caption("Preview only — nothing is charged until you submit.")
        if st.button("Submit auction round", type="primary", disabled=not editable,
                     help="Locks in this allocation and applies the net credit change."):
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
    _round_gate("Market Events", team)
    _guide(
        "Each round the Director introduces a market event — a competitor move, a rule change, "
        "a cost shock. These aren't random punishments: each one targets an assumption hidden "
        "in your canvas. Read the event, find which of your assumptions it threatens, and "
        "respond by testing, adjusting your model, or filing a pivot. Nothing to enter here — "
        "this page is your inbox.",
        terms=[
            ("Assumption exposed", "The belief this event puts pressure on. Go check whether "
             "you have evidence for it."),
            ("Broadcast", "An event sent to all teams at once."),
        ],
    )
    evs = db.list_events(team["id"])
    if not evs:
        st.info("No market events yet. The Director issues these starting around week 7.")
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
    editable = _round_gate("Pivot Petition", team)
    _guide(
        "A pivot is a deliberate change of direction backed by evidence — not just swapping to "
        "a new idea because the old one struggled. You can't simply declare a pivot; you file a "
        "petition and the investment committee (the Director) approves, approves conditionally, "
        "asks for more evidence, or rejects it. Fill in every field so the committee can see the "
        "change is driven by learning.",
        steps=[
            "Name the original assumption that turned out to be wrong.",
            "Cite the evidence that challenged it.",
            "Say which canvas block changes and what the change is.",
            "List the new assumptions the change creates and the evidence you'd need.",
            "Submit — then check back for the committee's decision.",
        ],
        terms=[
            ("Pivot", "A structured change to the business model based on what you learned."),
            ("Affected block", "Which canvas box changes (e.g. Customer Segment, Channel)."),
            ("Committee decision", "Approved, Conditional, Needs Evidence, Rejected, or "
             "'Random Change' if it looks unjustified."),
        ],
    )

    with st.form("pivot_form", clear_on_submit=True):
        original = st.text_area(
            "Original assumption",
            help="The belief you built on that the evidence has now undermined.")
        challenge = st.text_area(
            "Evidence that challenged it",
            help="What did you learn that shows the original assumption was wrong?")
        block = st.text_input(
            "Value Proposition / Business Model block affected",
            help="Which canvas box changes — e.g. Customer Segment, Channel, Revenue Stream.")
        change = st.text_area(
            "Proposed change",
            help="Exactly what you want to change the model to.")
        cost = st.number_input(
            "Cost of the change ($)", min_value=0.0, value=0.0, step=50.0,
            help="Estimated capital the pivot requires. The committee may charge this if approved.")
        new_assums = st.text_area(
            "New assumptions this creates",
            help="A pivot creates fresh beliefs to test. List them here.")
        needed = st.text_area(
            "Evidence required to support the new direction",
            help="What evidence would prove the new direction works?")
        if st.form_submit_button("Submit pivot petition", disabled=not editable,
                                 help="Send this to the investment committee for a decision."):
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
    st.caption("Watch the status and read the committee's note.")
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
    _guide(
        "Each student keeps their own journal so learning is individual, not just the team's. "
        "After each round, write a short entry: what you expected, what happened, and what you "
        "personally contributed. These entries feed your individual grade and your end-of-term "
        "Venture Defense, so write them for yourself even when the team disagrees.",
        steps=[
            "Enter your name and the round number.",
            "Answer each reflection prompt honestly in a sentence or two.",
            "Submit. Entries are saved and visible to the Director.",
        ],
        terms=[
            ("Decision journal", "Your personal record of decisions, evidence, and learning."),
            ("My contribution", "What YOU specifically did or argued — this protects against "
             "free-riding."),
        ],
    )

    with st.form("reflection_form", clear_on_submit=True):
        name = st.text_input(
            "Your name", help="Your own name — each journal entry is individual.")
        rnd = st.number_input(
            "Round", min_value=1, max_value=logic.total_rounds(), value=db.current_round(),
            help="Which simulation round this reflection is about.")
        expected = st.text_area(
            "What did we expect?", help="Before the round, what did your team predict would happen?")
        occurred = st.text_area(
            "What occurred?", help="What actually happened, including any surprises?")
        assumption = st.text_area(
            "Which assumption shaped our decision?",
            help="The key belief behind the choice your team made.")
        overlooked = st.text_area(
            "What evidence did we overlook?",
            help="Looking back, what information did you miss or discount?")
        differently = st.text_area(
            "What would we do differently?", help="A concrete change for next time.")
        contribution = st.text_area(
            "What did I personally contribute?",
            help="Your individual role in the decision — what you did, argued, or built.")
        if st.form_submit_button("Submit reflection",
                                 help="Save your individual journal entry for this round."):
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


# --------------------------------------------------------------------------- #
# AI Assist Log — generative AI use + AUDIT verification
# --------------------------------------------------------------------------- #
def ai_assist(team):
    st.subheader("🤖 AI Assist Log")
    _guide(
        "You're expected to use generative AI every round — to draft canvases, brainstorm "
        "propositions, design experiments, and more. But fluent AI text is NOT evidence: it's "
        "confident opinion until you verify it. Log each AI use here and run it through the "
        "**AUDIT** check. An AI idea stays 'Unverified' (evidence strength 0) until a real-world "
        "test moves it up the evidence ladder.",
        steps=[
            "Record the tool area, your prompt, and the AI's key output.",
            "Work through AUDIT: Assumptions, Unsupported claims, Data/sources, Independent test.",
            "Design the cheapest real test, run it (Experiment Marketplace), and log the evidence.",
            "Come back and set status to Verified, Rejected, or Modified.",
        ],
        terms=[
            ("AUDIT", "Assumptions · Unsupported · Data/sources · Independent test · Translate."),
            ("Unverified", "AI output not yet tested — treat as strength 0, mere opinion."),
            ("Verified", "A real test supported it; now it's backed by ladder evidence."),
        ],
    )
    st.markdown(content.AI_PROTOCOL_SUMMARY)

    st.divider()
    with st.form("add_ai_log", clear_on_submit=True):
        st.markdown("**Log a new AI-assisted contribution**")
        c1, c2 = st.columns(2)
        rnd = c1.number_input("Round", 1, logic.total_rounds(), db.current_round(),
                              help="Which round you used AI in.")
        tool_area = c2.selectbox("Where did you use AI?", content.AI_TOOL_AREAS,
                                 help="Which part of the venture the AI helped with.")
        prompt = st.text_area("Your prompt", help="What you asked the AI (paste or paraphrase).")
        ai_output = st.text_area("AI output (key claims)",
                                 help="The main ideas/claims the AI produced that you're considering using.")
        st.markdown("**AUDIT check**")
        audit = {}
        for letter, name, desc in content.AI_AUDIT_STEPS:
            audit[letter] = st.text_area(f"{letter} — {name}", help=desc, key=f"audit_{letter}")
        status = st.selectbox("Status", content.AI_STATUS_OPTIONS,
                              help="Unverified until a real test supports it.")
        if st.form_submit_button("Log AI use", help="Save this AI contribution and its AUDIT."):
            db.add_ai_log(team["id"], {
                "round": int(rnd), "tool_area": tool_area, "prompt": prompt,
                "ai_output": ai_output, "audit_a": audit["A"], "audit_u": audit["U"],
                "audit_d": audit["D"], "audit_i": audit["I"], "audit_t": audit["T"],
                "status": status,
            })
            st.success("AI use logged. Verify it with a real test before relying on it.")
            st.rerun()

    logs = db.list_ai_logs(team["id"])
    if logs:
        unv = sum(1 for l in logs if l["status"] == "Unverified")
        st.divider()
        st.write(f"### AI log — {len(logs)} entries · {unv} unverified")
        for l in logs:
            icon = {"Verified": "✅", "Rejected": "❌", "Modified": "✏️"}.get(l["status"], "⏳")
            with st.expander(f"{icon} R{l['round']} · {l['tool_area']} · {l['status']} · {l['created_at']}"):
                st.write(f"**Prompt:** {l['prompt']}")
                st.write(f"**AI output:** {l['ai_output']}")
                st.markdown("**AUDIT**")
                st.write(f"- **A** Assumptions: {l['audit_a'] or '—'}")
                st.write(f"- **U** Unsupported: {l['audit_u'] or '—'}")
                st.write(f"- **D** Data/sources: {l['audit_d'] or '—'}")
                st.write(f"- **I** Independent test: {l['audit_i'] or '—'}")
                st.write(f"- **T** Translate to evidence: {l['audit_t'] or '—'}")
                new_status = st.selectbox(
                    "Update status", content.AI_STATUS_OPTIONS,
                    index=content.AI_STATUS_OPTIONS.index(l["status"]),
                    key=f"aist_{l['id']}",
                    help="Set to Verified only after a real test supported the AI's claim.")
                cc1, cc2 = st.columns(2)
                if cc1.button("Save status", key=f"aisv_{l['id']}"):
                    db.update_ai_log(l["id"], status=new_status)
                    st.rerun()
                if cc2.button("Delete", key=f"aidl_{l['id']}"):
                    db.delete_ai_log(l["id"])
                    st.rerun()
