"""
views_instructor.py — Venture Foundry Director (instructor) console.

Like the student views, every screen has a "How this page works" panel and every
input carries a hover-help (ⓘ) tooltip so a first-time instructor can run the
whole simulation without a separate manual.
"""

import random
from datetime import datetime, date, time

import streamlit as st

import db
import content
import logic


def _guide(what, steps=None, terms=None, expanded=False):
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
# Auto-Director — automate scoring / events / pivots from team input, with override
# --------------------------------------------------------------------------- #
def auto_director():
    st.subheader("🤖 Auto-Director")
    _guide(
        "Let the app play Director. It reads what each team actually submitted this round "
        "(canvases, evidence, experiments, assumptions, auction, AI logs) and predicts their "
        "performance — turning that into suggested dashboard scores, a market event aimed at "
        "each team's biggest untested risk, and a recommended decision for any pending pivot. "
        "Nothing is final until you apply it: review the suggestions, override anything, then "
        "apply per team or all at once. You can also let it run automatically each time the "
        "round advances.",
        steps=[
            "Turn on the kinds of decisions you want automated.",
            "Click Compute suggestions to see predicted scores, events, and pivot calls.",
            "Override any value, then Apply per team — or Apply all suggestions.",
            "Optionally enable 'Run automatically on round advance'.",
        ],
        terms=[
            ("Predicted performance", "Scores the app derives from each team's submitted work."),
            ("Override", "Change any suggested value before it's applied — you have final say."),
            ("Auto-run on advance", "Apply enabled automation whenever the round moves forward."),
        ],
    )

    # ---- Automation settings ------------------------------------------------
    st.write("### Automation settings")
    s1, s2, s3 = st.columns(3)
    with s1:
        auto_scoring = st.checkbox("Auto scoring", value=logic.auto_flag("auto_scoring_on"),
                                   help="Predict dashboard scores from team input.")
        auto_events = st.checkbox("Auto events", value=logic.auto_flag("auto_events_on"),
                                  help="Issue a market event aimed at each team's biggest risk.")
    with s2:
        auto_pivots = st.checkbox("Auto pivots", value=logic.auto_flag("auto_pivots_on"),
                                  help="Decide pending pivot petitions by recommendation.")
        auto_feedback = st.checkbox("Auto feedback emails", value=logic.auto_flag("auto_feedback_on"),
                                    help="Send each team a venture-review email to their Inbox.")
    with s3:
        auto_run = st.checkbox("Run on advance",
                               value=logic.auto_flag("auto_run_on_advance", default=False),
                               help="Apply the enabled automation automatically whenever the "
                                    "round advances (manually or on schedule).")
    if st.button("Save automation settings"):
        logic.set_auto_flag("auto_scoring_on", auto_scoring)
        logic.set_auto_flag("auto_events_on", auto_events)
        logic.set_auto_flag("auto_pivots_on", auto_pivots)
        logic.set_auto_flag("auto_feedback_on", auto_feedback)
        logic.set_auto_flag("auto_run_on_advance", auto_run)
        st.success("Settings saved.")

    # ---- Tunable scoring weights -------------------------------------------
    with st.expander("⚖️ Scoring weights — tune how each dimension is scored"):
        st.caption("Each predicted score is the heuristic value × this weight (1.0 = default). "
                   "Set a dimension to 0 to ignore it, or above 1 to emphasize it. Changes "
                   "affect all predicted scores immediately.")
        weights = logic.get_score_weights()
        new_weights = {}
        wc = st.columns(2)
        for i, (dim, meaning) in enumerate(content.DASHBOARD_DIMENSIONS):
            with wc[i % 2]:
                new_weights[dim] = st.slider(dim, 0.0, 2.0, float(weights.get(dim, 1.0)), 0.1,
                                             help=meaning, key=f"wt_{dim}")
        b1, b2 = st.columns(2)
        if b1.button("Save weights"):
            logic.set_score_weights(new_weights)
            st.success("Scoring weights saved.")
            st.rerun()
        if b2.button("Reset weights to 1.0"):
            logic.set_score_weights(logic.default_score_weights())
            st.success("Weights reset.")
            st.rerun()

    teams = db.list_teams()
    if not teams:
        st.info("No teams yet. Create teams on the Team Setup page first.")
        return

    rnd = db.current_round()
    st.divider()
    hc1, hc2, hc3 = st.columns([2, 1, 1])
    hc1.write(f"### Suggestions for Round {rnd}")
    if hc2.button("✉️ Send feedback to all", help="Email a venture review to every team's Inbox."):
        for t in teams:
            logic.send_feedback(t["id"], rnd)
        st.success("Feedback emails sent to all teams.")
        st.rerun()
    if hc3.button("⚡ Apply ALL suggestions", help="Run enabled automation for every team now."):
        logic.run_autopilot(rnd)
        st.success("Applied enabled automation to all teams.")
        st.rerun()

    avail = logic.available_dimensions(rnd)
    not_yet = [d for d in content.DIMENSION_NAMES if d not in avail]
    st.caption(f"In play this round: {', '.join(avail)}."
               + (f"  Not yet introduced: {', '.join(not_yet)}." if not_yet else ""))
    events_open = rnd >= logic.page_unlock_round("Market Events")
    pivots_open = rnd >= logic.page_unlock_round("Pivot Petition")

    # ---- Per-team suggestions with override ---------------------------------
    for t in teams:
        sc = logic.auto_scores(t["id"], round_no=rnd)   # only in-play dimensions
        pred_val = logic.valuation_from_scores(t["id"], sc)
        with st.expander(f"{t['name']} — predicted valuation ${pred_val:,.0f}"):
            st.markdown("**Predicted dashboard scores** (only dimensions in play this round)")
            overrides = {}
            in_play = [(dim, m) for dim, m in content.DASHBOARD_DIMENSIONS if dim in sc]
            cols = st.columns(2)
            for i, (dim, _meaning) in enumerate(in_play):
                with cols[i % 2]:
                    overrides[dim] = st.slider(dim, 0, 100, int(sc[dim]),
                                               key=f"auto_sc_{t['id']}_{dim}")
            if not in_play:
                st.caption("No scored dimensions are in play yet at this round.")
            if in_play and st.button("Apply scores", key=f"auto_apply_sc_{t['id']}"):
                logic.apply_scores(t["id"], rnd, overrides)
                st.success(f"Scores applied to {t['name']} for Round {rnd}.")
                st.rerun()

            # Suggested event (only once market events are introduced)
            st.markdown("**Suggested market event**")
            if not events_open:
                st.caption(f"Market events are introduced in Round "
                           f"{logic.page_unlock_round('Market Events')} — none suggested yet.")
            else:
                ev = logic.suggest_event(t["id"], rnd)
                st.caption(ev["reason"])
                ecat = st.selectbox(
                    "Category", list(content.MARKET_EVENTS.keys()),
                    index=list(content.MARKET_EVENTS.keys()).index(ev["category"]),
                    key=f"auto_ecat_{t['id']}")
                opts = content.MARKET_EVENTS[ecat]
                texts = [o[0] for o in opts]
                default_i = texts.index(ev["text"]) if ev["text"] in texts else 0
                eidx = st.selectbox("Event", range(len(opts)),
                                    format_func=lambda i, o=opts: o[i][0],
                                    index=default_i, key=f"auto_eidx_{t['id']}")
                etext, eexp = opts[eidx]
                st.caption(f"Exposes: {eexp}")
                if st.button("Issue this event", key=f"auto_issue_{t['id']}"):
                    db.add_event(t["id"], rnd, ecat, etext, eexp)
                    st.success(f"Event issued to {t['name']}.")
                    st.rerun()

            # Feedback email — preview & send
            st.markdown("**Feedback email (venture review)**")
            fb = logic.generate_feedback(t["id"], rnd, sc)
            with st.popover("Preview / edit"):
                subj = st.text_input("Subject", value=fb["subject"], key=f"fb_subj_{t['id']}")
                body = st.text_area("Body", value=fb["body"], height=260, key=f"fb_body_{t['id']}")
                if st.button("Send to team Inbox", key=f"fb_send_{t['id']}"):
                    db.add_message(t["id"], subj, body, rnd)
                    st.success("Sent.")
            if st.button("Send suggested feedback", key=f"fb_quick_{t['id']}"):
                logic.send_feedback(t["id"], rnd, sc)
                st.success(f"Feedback sent to {t['name']}.")

            # Pending pivots (only once pivots are introduced)
            pend = [p for p in db.list_pivots(t["id"]) if p["status"] == "Submitted"]
            if pend and pivots_open:
                st.markdown("**Pending pivot petitions**")
                for p in pend:
                    dec, note = logic.recommend_pivot(p)
                    st.write(f"“{p['proposed_change'][:60]}” → recommended: **{dec}**")
                    st.caption(note)
                    chosen = st.selectbox(
                        "Decision", content.PIVOT_DECISIONS,
                        index=content.PIVOT_DECISIONS.index(dec),
                        key=f"auto_pdec_{p['id']}")
                    if st.button("Apply decision", key=f"auto_papply_{p['id']}"):
                        db.decide_pivot(p["id"], chosen, "[auto] " + note)
                        if chosen in ("Approved", "Conditional") and (p["change_cost"] or 0):
                            db.adjust_resources(t["id"], money=-p["change_cost"], kind="pivot",
                                                description="Pivot change cost (auto)",
                                                allow_negative=True)
                        st.success("Decision recorded.")
                        st.rerun()


# --------------------------------------------------------------------------- #
# Schedule & timing — number of rounds, topic order, advance date/times
# --------------------------------------------------------------------------- #
def schedule():
    st.subheader("🗓️ Schedule & Timing")
    _guide(
        "Design the whole run here. Each round can cover ONE OR MORE pieces of material, so you "
        "can fit all of the curriculum into however many rounds your class actually meets — pack "
        "the 15 topics into 7 rounds, or spread them out, whatever fits. Add material to a round, "
        "remove it, or move it to a different round. Any topic not placed sits in the 'Unassigned "
        "material' pool at the bottom until you slot it in. You can also set a date/time for a "
        "round to begin (applied the next time the app is opened after that time).",
        steps=[
            "Set how many rounds your class runs and click Apply & auto-balance.",
            "Review the suggested balanced arrangement; Apply it if you like it.",
            "Fine-tune by moving individual concepts between rounds.",
            "Optionally set an advance date/time per round.",
        ],
        terms=[
            ("Material / topic", "One curriculum unit (e.g. 'Customer discovery'). A round can "
             "hold several."),
            ("Load", "How much material a round holds (its concepts + objectives). Balancing "
             "keeps the heaviest round as light as possible."),
            ("Balanced arrangement", "Splits the curriculum, in logical order, into even-load "
             "rounds so no round is heavier than another."),
            ("Advance at", "When the sim moves TO that round, applied on next app load."),
        ],
    )

    total = logic.total_rounds()
    c1, c2 = st.columns([1, 2])
    with c1:
        new_total = st.number_input(
            "Number of rounds", 1, 40, total,
            help="How many rounds your class runs. Default 15. Applying auto-balances the "
                 "curriculum across that many rounds so no round is overloaded.")
        if st.button("Apply & auto-balance"):
            n = int(new_total)
            logic.set_total_rounds(n)
            logic.apply_layout(logic.suggest_balanced_layout(n))
            st.success(f"Schedule set to {n} rounds and balanced by logical content.")
            st.rerun()
    with c2:
        unplaced = logic.unassigned_topics()
        st.caption(f"Current round: **{db.current_round()}** of {total}.")
        st.caption(f"Curriculum coverage: **{len(content.CURRICULUM_TOPICS) - len(unplaced)}"
                   f"/{len(content.CURRICULUM_TOPICS)}** topics placed.")
        loads = [logic.round_load(r["round"]) for r in logic.get_schedule()]
        if loads:
            st.caption(f"Round load — min {min(loads)}, max {max(loads)} "
                       f"(closer together = more balanced).")
        nxt = logic.next_scheduled_advance()
        if nxt:
            st.caption(f"⏱️ Next auto-advance: Round {nxt[0]} at {nxt[1]}.")

    # ---- Suggested balanced arrangement ------------------------------------
    st.divider()
    st.write("### ✨ Suggested balanced arrangement")
    st.caption("Keeps concepts in their logical order and splits them into even-load rounds so "
               "no round is heavier than another. Preview below — apply it, then move anything "
               "you want by hand.")
    suggestion = logic.suggest_balanced_layout(total)
    summary = logic.layout_load_summary(suggestion)
    st.dataframe(
        [{"Round": s["round"], "Material": s["titles"], "Concepts+objectives (load)": s["load"]}
         for s in summary],
        use_container_width=True, hide_index=True,
    )
    if summary:
        sload = [s["load"] for s in summary]
        st.caption(f"Suggested load spread: min {min(sload)}, max {max(sload)}.")
    if st.button("✨ Apply suggested balanced arrangement"):
        logic.apply_layout(suggestion)
        st.success("Applied the balanced arrangement. Move any concept below to fine-tune.")
        st.rerun()

    round_choices = list(range(1, total + 1))
    unplaced = logic.unassigned_topics()

    st.divider()
    st.write("### Rounds")
    for row in logic.get_schedule():
        rnd = row["round"]
        names = " + ".join(t["title"] for t in row["topics"]) or "— empty —"
        with st.expander(f"Round {rnd} · load {logic.round_load(rnd)} — {names}"):
            # Existing material: remove or move each item.
            if row["topics"]:
                for tp in row["topics"]:
                    mc1, mc2, mc3 = st.columns([3, 1.4, 1])
                    mc1.markdown(f"**{tp['title']}**")
                    mc1.caption(tp["class_focus"])
                    move_to = mc2.selectbox(
                        "Move to round", round_choices,
                        index=rnd - 1, key=f"move_{rnd}_{tp['key']}",
                        label_visibility="collapsed",
                        help="Send this material to a different round.")
                    if mc2.button("Move", key=f"movebtn_{rnd}_{tp['key']}"):
                        db.set_topic_placement(tp["key"], int(move_to))
                        st.rerun()
                    if mc3.button("Remove", key=f"rmvbtn_{rnd}_{tp['key']}",
                                  help="Unassign (moves it to the pool)."):
                        db.remove_round_topic(tp["key"])
                        st.rerun()
            else:
                st.caption("No material assigned to this round yet.")

            # Add material to this round (from the unassigned pool).
            if unplaced:
                ac1, ac2 = st.columns([3, 1])
                add_key = ac1.selectbox(
                    "Add material", [t["key"] for t in unplaced],
                    format_func=lambda k: content.CURRICULUM_BY_KEY[k]["title"],
                    key=f"add_{rnd}", label_visibility="collapsed",
                    help="Pick unassigned material to add to this round.")
                if ac2.button("Add", key=f"addbtn_{rnd}"):
                    db.set_topic_placement(add_key, rnd)
                    st.rerun()
            else:
                st.caption("All curriculum material is placed. ✔")

            # Advance date/time for this round.
            cur_dt = logic._parse_dt(row["advance_at"])
            set_time = st.checkbox("Schedule an advance date/time", value=cur_dt is not None,
                                   key=f"sch_chk_{rnd}",
                                   help="Tick to auto-advance TO this round at a set time.")
            if set_time:
                d = st.date_input("Advance date",
                                  value=(cur_dt.date() if cur_dt else date.today()),
                                  key=f"sch_date_{rnd}")
                t = st.time_input("Advance time",
                                  value=(cur_dt.time() if cur_dt else time(9, 0)),
                                  key=f"sch_time_{rnd}")
                if st.button("Save advance time", key=f"sch_save_{rnd}"):
                    db.set_schedule_advance(rnd, datetime.combine(d, t).isoformat(timespec="minutes"))
                    st.success(f"Round {rnd} advance time saved.")
                    st.rerun()
            elif cur_dt is not None and st.button("Clear advance time", key=f"sch_clr_{rnd}"):
                db.set_schedule_advance(rnd, None)
                st.rerun()

    # Unassigned material pool.
    st.divider()
    st.write("### Unassigned material")
    if not unplaced:
        st.success("Every curriculum topic is assigned to a round. ✔")
    else:
        st.caption("These topics are not yet in any round — place them so students see them.")
        for tp in unplaced:
            uc1, uc2, uc3 = st.columns([3, 1.4, 1])
            uc1.markdown(f"**{tp['title']}**")
            uc1.caption(", ".join(tp["concepts"]))
            to_round = uc2.selectbox(
                "Round", round_choices, key=f"place_{tp['key']}",
                label_visibility="collapsed")
            if uc3.button("Place", key=f"placebtn_{tp['key']}"):
                db.set_topic_placement(tp["key"], int(to_round))
                st.rerun()

    st.divider()
    if st.button("↩️ Reset to default (15 rounds, one topic each)"):
        logic.set_total_rounds(content.DEFAULT_TOTAL_ROUNDS)
        for tp in content.CURRICULUM_TOPICS:
            db.remove_round_topic(tp["key"])
        for i, key in enumerate(content.DEFAULT_TOPIC_ORDER):
            db.set_topic_placement(key, i + 1, 0)
            db.set_schedule_advance(i + 1, None)
        st.success("Schedule reset to the default order.")
        st.rerun()


# --------------------------------------------------------------------------- #
# Round control & semester map
# --------------------------------------------------------------------------- #
def round_control():
    st.subheader("🎛️ Round & Semester Control")
    _guide(
        "You are the Venture Foundry Director. **This is where you advance the cohort to the "
        "next round — which is what unlocks the next round's tools for every team.** There are "
        "two ways to advance: click the Advance button here whenever you're ready, or set a "
        "date/time on Schedule & Timing and let it advance automatically. The current round is "
        "stamped onto events, scores, and reflections.",
        steps=[
            "When the class is ready for the next week, click ▶️ Advance to the next round.",
            "Advancing unlocks that round's tools, applies learning, resets founder hours, and "
            "charges any specialist salaries.",
            "To move without going in order, use 'Jump to a specific round'.",
            "Prefer automatic? Set advance date/times on Schedule & Timing.",
        ],
        terms=[
            ("Advance", "Move the whole cohort to the next round and unlock its tools."),
            ("Round", "The current simulation week. Everything new is tagged with it."),
            ("Instructor PIN", "The password teams cannot see; it opens this Director console."),
        ],
    )
    cur = db.current_round()
    total = logic.total_rounds()

    # ---- Advance / rewind (the main action of this page) --------------------
    st.markdown(f"## 📍 Cohort is on **Round {cur} of {total}**")

    def _unlocks_for(rnd):
        tools = [p for p in logic.newly_unlocked(rnd) if p not in content.BASE_TOOLS]
        titles = [t["title"] for t in logic.topics_for_round(rnd)]
        return tools, titles

    if cur < total:
        ntools, ntitles = _unlocks_for(cur + 1)
        st.markdown(f"### ▶️ Advance the cohort to Round {cur + 1}")
        if ntitles:
            st.caption("Next round covers: **" + " + ".join(ntitles) + "**")
        if ntools:
            st.caption("Unlocks these tools for every team: **" + ", ".join(ntools) + "**")
        else:
            st.caption("No new tools unlock next round — teams keep refining current work.")
        ac1, ac2 = st.columns([2, 3])
        if ac1.button(f"▶️ Advance to Round {cur + 1}", type="primary",
                      help="Moves the whole cohort forward one round and unlocks its tools."):
            new_r = cur + 1
            db.set_setting("current_round", new_r)
            logic.on_round_change(new_r)   # apply learning, reset hours, charge salaries
            msg = f"Advanced to Round {new_r} — its tools are now unlocked for all teams."
            if logic.auto_flag("auto_run_on_advance", default=False):
                logic.run_autopilot(new_r)
                msg += " Auto-Director applied."
            st.success(msg)
            st.rerun()
        ac2.caption("Do this once your class has finished the current round's work (and any "
                    "decision deadline has passed).")
    else:
        st.success(f"🏁 You're on the final round ({total}). Add more rounds on Schedule & "
                   "Timing if your course needs them.")

    with st.expander("↔️ Go back a round or jump to a specific round"):
        jc1, jc2 = st.columns(2)
        if cur > 1 and jc1.button(f"◀️ Back to Round {cur - 1}",
                                  help="Return the cohort to the previous round."):
            db.set_setting("current_round", cur - 1)
            st.warning(f"Moved back to Round {cur - 1}.")
            st.rerun()
        with jc2:
            jump = st.number_input("Jump to round", 1, total, min(cur, total),
                                   help="Set any round directly (non-sequential).")
            if st.button("Set round", help="Apply this exact round to the whole cohort."):
                advanced = int(jump) > cur
                db.set_setting("current_round", int(jump))
                logic.on_round_change(int(jump))
                msg = f"Round set to {jump}."
                if advanced and logic.auto_flag("auto_run_on_advance", default=False):
                    logic.run_autopilot(int(jump))
                    msg += " Auto-Director applied."
                st.success(msg)
                st.rerun()

    nxt = logic.next_scheduled_advance()
    if nxt:
        st.info(f"⏱️ **Automatic advance scheduled:** Round {nxt[0]} at {nxt[1]} — applies the "
                "next time the app is opened after that time. (You can still advance manually "
                "above at any point.)")
    else:
        st.caption("💡 No automatic advance is scheduled. Advance manually above, or set "
                   "date/times on **Schedule & Timing** to automate it.")

    # ---- Console settings ----------------------------------------------------
    st.divider()
    st.markdown("### ⚙️ Console settings")
    c2a, c2b = st.columns(2)
    with c2a:
        pin = st.text_input(
            "Instructor PIN (change)", value=db.get_setting("instructor_pin", "foundry"),
            help="The password for this Director console. Change it from the default 'foundry' "
                 "so students can't open it.")
        if st.button("Update PIN", help="Save the new instructor PIN."):
            db.set_setting("instructor_pin", pin)
            st.success("PIN updated.")
    with c2b:
        strict = st.checkbox(
            "Strict round mode", value=logic.strict_round_mode(),
            help="When on, students can only edit tools relevant to the current round; tools "
                 "from other rounds are view-only, and not-yet-introduced tools are locked. "
                 "Turn off to let teams edit any unlocked tool anytime.")
        if st.button("Save round mode"):
            logic.set_auto_flag("strict_round_mode", strict)
            st.success("Round mode saved.")

    # ---- Economy & balance --------------------------------------------------
    with st.expander("💲 Economy & balance — tune the numbers"):
        st.caption("Adjust the simulation's costs without editing code. Changes apply "
                   "immediately to all teams.")
        econ = logic.get_economy()

        st.markdown("**Founder time**")
        e1, e2 = st.columns(2)
        cur_hpw = int(float(db.get_setting("econ_hours_per_week", "60") or 60))
        hpw = e1.number_input(
            "Founder-hours per WEEK (raw, all teams)",
            content.FULL_PRODUCTIVITY_HOURS, content.MAX_WEEKLY_HOURS, cur_hpw,
            help="Raw weekly hours (40–80). Resets each round — unused hours are lost. "
                 "Productivity drops past 40h, so effective time grows slowly.")
        train_mult = e2.number_input(
            "Training cost per level (hours × level)", 1, 60, int(econ["train_mult"]),
            help="Founder-hours to raise a skill = (target level) × this. Higher = training is "
                 "more of a commitment.")

        st.markdown("**Hiring — part-time specialist**")
        p1, p2, p3 = st.columns(3)
        pt_boost = p1.number_input("PT skill boost", 1, 5, int(econ["pt_boost"]), key="pt_b")
        pt_up = p2.number_input("PT upfront $", 0, 5000, int(econ["pt_upfront"]), step=50, key="pt_u")
        pt_pr = p3.number_input("PT salary $/round", 0, 2000, int(econ["pt_per_round"]), step=20, key="pt_p")

        st.markdown("**Hiring — full-time specialist**")
        f1, f2, f3 = st.columns(3)
        ft_boost = f1.number_input("FT skill boost", 1, 5, int(econ["ft_boost"]), key="ft_b")
        ft_up = f2.number_input("FT upfront $", 0, 8000, int(econ["ft_upfront"]), step=50, key="ft_u")
        ft_pr = f3.number_input("FT salary $/round", 0, 3000, int(econ["ft_per_round"]), step=20, key="ft_p")

        if st.button("Save economy settings"):
            logic.set_economy({
                "train_mult": train_mult,
                "pt_boost": pt_boost, "pt_upfront": pt_up, "pt_per_round": pt_pr,
                "ft_boost": ft_boost, "ft_upfront": ft_up, "ft_per_round": ft_pr,
            })
            db.set_setting("econ_hours_per_week", int(hpw))
            for t in db.list_teams():
                db.update_team(t["id"], hours_per_round=int(hpw))
            st.success("Economy settings saved and applied to all teams.")

        st.caption("Difficulty presets (starting weekly hours) live in content.py: "
                   + ", ".join(f"{k} {v['hours']}h" for k, v in content.DIFFICULTY_LEVELS.items()))

    st.divider()
    topics = logic.topics_for_round(cur)
    if topics:
        st.write(f"### This round's plan — Round {cur}")
        st.caption("Teach the concepts in the first session; the second session is the "
                   "simulation round. A round may cover several pieces of material.")
        for tp in topics:
            st.info(f"**{tp['title']}** — {tp['class_focus']}\n\n"
                    f"Task: {tp['sim_task']}  ·  Tool: {tp['tool']}")
            cc1, cc2 = st.columns(2)
            with cc1:
                st.markdown("**Learning objectives**")
                for o in tp["objectives"]:
                    st.markdown(f"- {o}")
            with cc2:
                st.markdown("**Concepts introduced**")
                for c in tp["concepts"]:
                    st.markdown(f"- {c}")
        newly = [p for p in logic.newly_unlocked(cur) if p not in content.BASE_TOOLS]
        if newly:
            st.success("🔓 Tools introduced to students this round: " + ", ".join(newly))
    else:
        st.warning("No material is assigned to this round. Add some on Schedule & Timing.")

    st.divider()
    st.write(f"### {total}-round map")
    st.caption("The current schedule. Add/remove/move material, change the number of rounds, "
               "and set advance times on the **Schedule & Timing** page.")
    st.dataframe(
        [{"Round": row["round"],
          "Material": " + ".join(t["title"] for t in row["topics"]) or "—",
          "Advance at": row["advance_at"] or "—"}
         for row in logic.get_schedule()],
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

    # ---- Quick balanced setup ------------------------------------------------
    st.write("### ⚡ Quick balanced setup")
    st.caption("Create a whole cohort in one step. Every team gets IDENTICAL starting "
               "resources for the chosen difficulty, so all teams have the same opportunity "
               "for success. Territories and founder styles can vary for flavor without "
               "changing anyone's odds.")
    with st.form("quick_setup", clear_on_submit=False):
        q1, q2 = st.columns(2)
        n_teams = q1.number_input(
            "Number of teams", 1, 12, 4,
            help="How many teams to create. Each is named with the prefix below plus a number.")
        difficulty = q2.selectbox(
            "Difficulty level", content.DIFFICULTY_ORDER,
            index=content.DIFFICULTY_ORDER.index("Standard"),
            help="Sets the starting capital, credits, hours, and market ceiling for EVERY "
                 "team. Novice = generous; Expert = ruthless scarcity.")
        preset = content.DIFFICULTY_LEVELS[difficulty]
        st.info(
            f"**{difficulty}** — {preset['blurb']}\n\n"
            f"Each team starts with **${preset['capital']:,} capital · "
            f"{preset['credits']} Evidence Credits · {preset['hours']} founder-hours · "
            f"${preset['market_potential']:,} market potential.**")

        q3, q4 = st.columns(2)
        opp_mode_label = q3.radio(
            "Opportunity territories", ["Distinct per team", "Same for all teams"],
            help="Distinct = each team gets a different problem area (avoids teams competing "
                 "for the identical customers). Same = every team tackles one shared territory "
                 "(maximum comparability). Odds of success are equal either way.")
        opp_mode = "same" if opp_mode_label == "Same for all teams" else "distinct"
        opp_choice = None
        if opp_mode == "same":
            opp_choice = q3.selectbox(
                "Shared territory", content.OPPORTUNITY_TERRITORIES,
                help="The single territory all teams will work in.")
        founder_mode_label = q4.radio(
            "Founder cards", ["Same balanced card", "Varied archetypes"],
            help="Balanced = every team gets the same neutral, well-rounded founder card "
                 "(most equal). Varied = teams get different founder styles for flavor, but "
                 "their money and hours are still forced equal.")
        founder_mode = "balanced" if founder_mode_label == "Same balanced card" else "varied"

        q5, q6 = st.columns(2)
        prefix = q5.text_input(
            "Team name prefix", value="Team",
            help="Teams are named like 'Team 1', 'Team 2', …")
        clear_existing = q6.checkbox(
            "Delete existing teams first", value=False,
            help="Tick to start a clean cohort. WARNING: this permanently removes all current "
                 "teams and their data.")

        if st.form_submit_button("Generate balanced cohort",
                                 help="Create all teams at once with equal starting resources."):
            created = logic.quick_setup_teams(
                n_teams, difficulty, opp_mode, opp_choice, founder_mode, prefix, clear_existing)
            st.success(f"Created {len(created)} teams at **{difficulty}** difficulty. "
                       "Give each team its join code below.")
            st.table([{"Team": c["name"], "Join code": c["code"], "Territory": c["territory"]}
                      for c in created])

    st.divider()
    st.write("### ➕ Add a single team manually")
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
            new_team = db.get_team_by_code(code)
            b = logic.default_build(db.get_team(new_team["id"]))
            db.update_team(new_team["id"], build_budget=b, founder_hours=b)
            logic.send_welcome(new_team["id"])   # Round-1 welcome + hints in the Inbox
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

            # ---- Round-1 welcome email — preview, edit before students see it ----
            st.markdown("**Welcome email (Round-1 onboarding)**")
            st.caption("Auto-written from this team's founder card, territory, and Round-1 "
                       "hints. Preview and tweak the wording before it lands in their Inbox.")
            wsent = any("Welcome" in m["subject"] for m in db.list_messages(t["id"]))
            wel = logic.generate_welcome(t["id"])
            with st.popover("Preview / edit welcome email"):
                wsubj = st.text_input("Subject", value=wel["subject"], key=f"wel_subj_{t['id']}")
                wbody = st.text_area("Body", value=wel["body"], height=340,
                                     key=f"wel_body_{t['id']}")
                st.caption("Preview:")
                st.markdown(wbody)
                if st.button("Send this welcome to the team Inbox", key=f"wel_send_{t['id']}"):
                    db.add_message(t["id"], wsubj, wbody, 1)
                    st.success("Welcome email sent.")
                    st.rerun()
            wc1, wc2 = st.columns(2)
            if wc1.button("Resend suggested welcome", key=f"wel_quick_{t['id']}",
                          help="Send the auto-written welcome email as-is to this team's Inbox."):
                logic.send_welcome(t["id"])
                st.success("Welcome email sent.")
            wc2.caption("✅ Already sent" if wsent else "✉️ Not sent yet")


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
            "Round", 1, logic.total_rounds(), db.current_round(),
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
            "Round", 1, logic.total_rounds(), db.current_round(),
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
# Round Scores — one automated 0–100 grade per team for the committed round work
# --------------------------------------------------------------------------- #
def _round_score_email(team, rnd, rs):
    comp = rs["components"]
    _labels = {"commitment": "Commitment / completion", "evidence": "Evidence quality",
               "coherence": "Model coherence", "concepts": "Concept coverage",
               "ai_verification": "AI verification"}
    lines = [f"Round {rnd} score for {team['name']}: {rs['score']:.0f}/100 "
             f"({rs['grade']}).", "",
             "How it breaks down (only what you could do this round is counted):"]
    for k in logic.ROUND_SCORE_COMPONENTS:
        if comp[k] is None:
            lines.append(f"  • {_labels[k]}: not available this round (not counted)")
        else:
            lines.append(f"  • {_labels[k]}: {comp[k]:.0f}")
    if rs.get("concept_answered"):
        lines.append(f"    (of your concept answers, {rs['concept_aligned']}/"
                     f"{rs['concept_answered']} were tied to your territory/venture — "
                     "answers grounded in your business score higher)")
    if rs["penalty"]:
        lines.append(f"  • Risk penalty: -{rs['penalty']:.0f} "
                     f"({rs['exposed_assumptions']} important untested assumption(s))")
    lines += ["", ("You committed this round's work before scoring." if rs["committed"]
                   else "Note: this round was scored on your work as-is (not formally committed)."),
              "", "— The Venture Foundry Director"]
    return {"subject": f"Round {rnd} score — {team['name']}", "body": "\n".join(lines)}


def round_scores():
    st.subheader("🏁 Round Scores (out of 100)")
    _guide(
        "This gives every team a single automated 0–100 grade for the work they committed in a "
        "round. It blends up to four things — how much of the round's required work is complete "
        "(commitment), the strength of their evidence, their business-model coherence, and how "
        "many of the round's concepts they covered — then subtracts a penalty for important "
        "assumptions they've left untested. **Only what a team could actually do that round is "
        "counted:** evidence and coherence are skipped (shown as n/a) until their tools are "
        "introduced, and the weights renormalize over what's left, so no one is marked down for "
        "a tool they don't have yet. **Concept answers that align with the team's territory and "
        "the venture they're building score higher than generic answers.**",
        steps=[
            "Set the four component weights (they're normalized, so relative size is what counts).",
            "Set the strictness dial: left is lenient, right is harsh.",
            "Pick the round and read the table — each team's score updates live.",
            "Optionally email any team its score breakdown.",
        ],
        terms=[
            ("Commitment", "Share of the round's decisions + concept-checks completed."),
            ("Counted this round", "Only components whose tools exist by this round are graded; "
             "others show n/a and don't lower the score."),
            ("Alignment", "Concept answers referencing the team's own territory/venture count "
             "fully; generic answers count partially."),
            ("Strictness", "A curve on the final score: lenient lifts scores, strict compresses them."),
            ("Risk penalty", "Points removed for important, still-untested assumptions."),
        ],
    )
    teams = db.list_teams()
    if not teams:
        st.info("No teams yet. Create teams on the Team Setup page first.")
        return

    cfg = logic.get_round_score_config()

    # ---- Sensitivity controls ------------------------------------------------
    st.markdown("### 🎚️ Scoring sensitivity")
    labels = {"commitment": "Commitment / completion", "evidence": "Evidence quality",
              "coherence": "Model coherence", "concepts": "Concept coverage",
              "ai_verification": "AI verification"}
    with st.form("round_score_cfg"):
        cols = st.columns(len(logic.ROUND_SCORE_COMPONENTS))
        new_w = {}
        for i, k in enumerate(logic.ROUND_SCORE_COMPONENTS):
            hlp = ("Rewards actually EVALUATING AI use (verified/rejected/modified), not just "
                   "logging it. Only counts once a team has used AI."
                   if k == "ai_verification" else f"Relative weight of {labels[k].lower()}.")
            new_w[k] = cols[i].slider(labels[k], 0, 100, int(cfg["weights"][k]), help=hlp)
        strict = st.slider(
            "Strictness (← lenient · harsh →)", 0, 100, int(cfg["strictness"]),
            help="50 is neutral. Below 50 lifts scores (forgiving); above 50 makes high "
                 "scores harder to reach (demanding).")
        wsum = sum(new_w.values()) or 1
        st.caption("Normalized weights: " + " · ".join(
            f"{labels[k]} {100*new_w[k]/wsum:.0f}%" for k in logic.ROUND_SCORE_COMPONENTS))
        c1, c2 = st.columns(2)
        if c1.form_submit_button("Save sensitivity", help="Apply these settings to all scores."):
            logic.set_round_score_config(new_w, strict)
            st.success("Saved.")
            st.rerun()
        if c2.form_submit_button("Reset to defaults"):
            d = logic.default_round_score_config()
            logic.set_round_score_config(d["weights"], d["strictness"])
            st.rerun()

    # ---- Scores table --------------------------------------------------------
    st.markdown("### 📋 Scores")
    rnd = st.number_input("Round to score", 1, logic.total_rounds(), db.current_round(),
                          help="Round scores are computed live from each team's current work.")
    rnd = int(rnd)
    ds = logic.deadline_status(rnd)
    if ds["set"]:
        st.caption(f"⏰ Decisions due: **{ds['due_text']}** "
                   + ("· deadline passed" if ds["passed"] else f"· {ds['remaining']}"))
    else:
        st.caption("🗓️ No decision deadline is set for this round (set advance times on "
                   "**Schedule & Timing**).")

    def _cell(v):
        return "n/a" if v is None else v

    rows = []
    scored = {}
    for t in teams:
        rs = logic.round_score(t["id"], rnd, cfg)
        scored[t["id"]] = rs
        c = rs["components"]
        rows.append({
            "Team": t["name"],
            "Score /100": rs["score"],
            "Grade": rs["grade"],
            "Commit": "✅" if rs["committed"] else "—",
            "Completion": _cell(c["commitment"]),
            "Evidence": _cell(c["evidence"]),
            "Coherence": _cell(c["coherence"]),
            "Concepts": _cell(c["concepts"]),
            "AI verify": _cell(c["ai_verification"]),
            "Risk −": rs["penalty"],
        })
    st.dataframe(sorted(rows, key=lambda r: r["Score /100"], reverse=True),
                 use_container_width=True, hide_index=True)
    _counted = logic.round_score_available(rnd)
    _off = [k for k, v in _counted.items() if not v]
    if _off:
        st.caption("**n/a** = a component isn't graded this round because its tool isn't "
                   "introduced yet, so teams aren't marked down for it. Not counted in Round "
                   f"{rnd}: " + ", ".join(_off) + ". (Weights are renormalized over what counts.)")
    st.caption("Scores recompute live from current work and your sensitivity settings above. "
               "**Concept answers that reference the team's territory/venture score higher than "
               "generic ones.**")

    # ---- Per-team detail + email --------------------------------------------
    st.markdown("### ✉️ Send a score to a team")
    team = st.selectbox("Team", teams, format_func=lambda t: t["name"],
                        key="rs_team", help="Preview and send this team's score email.")
    rs = scored[team["id"]]
    m1, m2, m3 = st.columns(3)
    m1.metric("Round score", f"{rs['score']:.0f}/100", rs["grade"])
    m2.metric("Committed?", "Yes" if rs["committed"] else "No")
    m3.metric("Risk penalty", f"-{rs['penalty']:.0f}")
    email = _round_score_email(team, rnd, rs)
    with st.popover("Preview / edit score email"):
        subj = st.text_input("Subject", value=email["subject"], key=f"rs_subj_{team['id']}")
        body = st.text_area("Body", value=email["body"], height=280, key=f"rs_body_{team['id']}")
        if st.button("Send to team Inbox", key=f"rs_send_{team['id']}"):
            db.add_message(team["id"], subj, body, rnd)
            st.success("Sent.")
    if st.button("Send suggested score to all teams", key="rs_send_all"):
        for t in teams:
            e = _round_score_email(t, rnd, scored[t["id"]])
            db.add_message(t["id"], e["subject"], e["body"], rnd)
        st.success(f"Sent Round {rnd} scores to every team.")


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
        flagged = sum(1 for e in db.list_evidence(t["id"])
                      if logic.evidence_flags(e["description"], e["source"], e["strength"]))
        rows.append({
            "Team": t["name"], "Stage": t["stage"], "Capital": f"${t['capital']:,.0f}",
            "Credits": round(t["evidence_credits"], 1), "Valuation": f"${val['valuation']:,.0f}",
            "Evidence-backed": f"{val['evidence_coverage']*100:.0f}%",
            "Evidence items": esum["count"], "Behavioral": esum["behavioral"],
            "⚠️ Flagged evidence": flagged,
            "High-risk untested": len(arep["exposed"]), "Experiments": eff["experiments"],
        })
    st.dataframe(rows, use_container_width=True, hide_index=True)
    st.caption("**Evidence-backed** = how much of the venture's value is earned by evidence "
               "(tested important assumptions + evidence strength); it discounts the valuation, "
               "so early rounds are low by design. **⚠️ Flagged evidence** = items whose wording "
               "may not match the strength the team chose (likely opinion logged as behavior, or "
               "vice-versa) — a coaching signal, not an automatic penalty.")

    # Fairness check — are all teams starting on equal footing?
    diff = db.get_setting("difficulty", "not set")
    bal = logic.cohort_balance(teams)
    if bal:
        if bal["balanced"]:
            st.success(f"⚖️ Balanced cohort — every team has identical starting resources "
                       f"(difficulty: **{diff}**). Equal opportunity for success.")
        else:
            st.warning(
                f"⚖️ Resources are uneven across teams (difficulty: **{diff}**). "
                f"Capital spread ${bal['capital']['spread']:,.0f}, "
                f"credits spread {bal['credits']['spread']}, "
                f"hours spread {bal['hours']['spread']}, "
                f"market-potential spread ${bal['market_potential']['spread']:,.0f}. "
                "This is expected once teams spend during play; large gaps at the START usually "
                "mean teams were created manually with different values — use Quick Setup for "
                "an equal-footing cohort.")

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
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["Canvases", "Assumptions", "Experiments", "Reflections", "AI use"])
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
    with tab5:
        logs = db.list_ai_logs(team["id"])
        unv = sum(1 for l in logs if l["status"] == "Unverified")
        st.caption(f"{len(logs)} AI-assist entries · {unv} still unverified. Check that teams "
                   "verify AI output with real evidence rather than accepting it as fact.")
        for l in logs:
            st.write(f"- **[{l['status']}]** R{l['round']} · {l['tool_area']}: "
                     f"{(l['ai_output'] or '')[:70]}")
            if l["audit_i"]:
                st.caption(f"   Test designed: {l['audit_i'][:80]}")
