"""
Venture Foundry — From hunch to hard evidence
A semester-long entrepreneurship simulation.

Run with:  streamlit run app.py

Two roles:
  • Student / Team — plays the venture (dashboard, canvases, assumptions,
    experiment marketplace, evidence ledger, events, pivots, reflections).
  • Venture Foundry Director (instructor) — sets up teams, controls rounds,
    issues market events, reviews pivot petitions, scores dashboards.

Data persists in a local SQLite database (venture_foundry.db).
Default instructor PIN: foundry  (change it in Director → Round Control).
"""

import os

import streamlit as st
import streamlit.components.v1 as components

import db
import content
import logic
import branding
import views_student as vs
import views_instructor as vi

# Browser-tab favicon: the Molten V logo (falls back to an emoji if unavailable).
_ICON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "favicon.png")
_PAGE_ICON = "🏭"
if os.path.exists(_ICON_PATH):
    try:
        from PIL import Image
        _PAGE_ICON = Image.open(_ICON_PATH)
    except Exception:
        _PAGE_ICON = _ICON_PATH

st.set_page_config(page_title="Venture Foundry — From hunch to hard evidence",
                   page_icon=_PAGE_ICON, layout="wide")

db.init_db()


def _sync_active_game():
    """Apply date-based auto-advance and round-change side effects for whichever game
    is currently active (a student's game, or the Director's selected game)."""
    prev = db.current_round()
    new = logic.maybe_auto_advance()
    logic.on_round_change(new)
    if new != prev and logic.auto_flag("auto_run_on_advance", default=False):
        logic.run_autopilot(new)
    return new


def _scroll_top_on_change(state_key, page):
    """Scroll the main pane to the top whenever the selected page changes."""
    if st.session_state.get(state_key) != page:
        st.session_state[state_key] = page
        components.html(
            "<script>var d=window.parent.document;"
            "['section.main','[data-testid=\"stMain\"]',"
            "'[data-testid=\"stAppViewContainer\"]'].forEach(function(s){"
            "var e=d.querySelector(s); if(e){e.scrollTo(0,0);}});"
            "window.parent.scrollTo(0,0);</script>",
            height=0,
        )

# --------------------------------------------------------------------------- #
# Session state
# --------------------------------------------------------------------------- #
st.session_state.setdefault("role", None)          # "student" | "instructor"
st.session_state.setdefault("team_id", None)
st.session_state.setdefault("instructor_ok", False)


def logout():
    st.session_state.role = None
    st.session_state.team_id = None
    st.session_state.instructor_ok = False


# --------------------------------------------------------------------------- #
# Landing / login
# --------------------------------------------------------------------------- #
def landing():
    branding.header()
    st.markdown(
        "> Students do not earn points for having a good idea. They earn resources by "
        "producing **credible evidence** that their business model could work."
    )
    st.write("A semester-long simulation integrating Strategyzer's Value Proposition "
             "Canvas, Business Model Canvas, assumption mapping, experimentation, and "
             "evidence-based pivoting.")

    tab_student, tab_instructor = st.tabs(["🎓 Enter as a Team", "🎩 Enter as Director"])

    with tab_student:
        st.write("Enter your team join code (issued by the Director).")
        code = st.text_input("Join code", key="join_code_input").strip().upper()
        if st.button("Join", type="primary"):
            team = db.get_team_by_code(code)
            if team:
                st.session_state.role = "student"
                st.session_state.team_id = team["id"]
                st.rerun()
            else:
                st.error("No team found with that code.")
        teams = db.list_teams()
        if teams:
            with st.expander("Instructor demo: pick a team directly"):
                t = st.selectbox("Team", teams, format_func=lambda t: f"{t['name']} ({t['join_code']})")
                if st.button("Enter selected team"):
                    st.session_state.role = "student"
                    st.session_state.team_id = t["id"]
                    st.rerun()

    with tab_instructor:
        pin = st.text_input("Instructor PIN", type="password", key="pin_input")
        if st.button("Open Director Console", type="primary"):
            if pin == db.get_setting("instructor_pin", "foundry"):
                st.session_state.role = "instructor"
                st.session_state.instructor_ok = True
                st.rerun()
            else:
                st.error("Incorrect PIN.")
        st.caption("Default PIN is `foundry` — change it after first login.")


# --------------------------------------------------------------------------- #
# Student shell
# --------------------------------------------------------------------------- #
STUDENT_PAGES = {
    "Round Briefing": vs.round_briefing,
    "Inbox": vs.inbox,
    "Dashboard": vs.dashboard,
    "Progress": vs.progress,
    "Leaderboard": vs.leaderboard,
    "Founder & Opportunity": vs.founder_opportunity,
    "Founder & Team": vs.founder_skills,
    "Canvases": vs.canvases,
    "VP Auction": vs.vp_auction,
    "Assumption Map": vs.assumptions,
    "Experiment Marketplace": vs.experiments,
    "Evidence Ledger": vs.evidence,
    "Market Events": vs.market_events,
    "Pivot Petition": vs.pivots,
    "Concept Check": vs.concept_check,
    "AI Assist Log": vs.ai_assist,
    "Decision Journal": vs.reflections,
    "Demo Day": vs.demo_day,
}


def _make_student_label(team):
    """Sidebar labels: lock/reference state + round tag + Inbox unread + commit badge."""
    unread = db.unread_count(team["id"])
    rnd = db.current_round()
    committed = logic.commitment_state(team["id"], rnd)["committed"]

    def label(page):
        if page == "Inbox":
            return f"Inbox 🔵{unread}" if unread else "Inbox"
        if page == "Round Briefing":
            # Surface commit status right where the commit control lives.
            return "Round Briefing ✅" if committed else "Round Briefing ⚠️"
        state = logic.tool_state(page, rnd, team["id"])
        if state == "locked":
            return f"🔒 {page} · R{logic.page_unlock_round(page)}"
        if state == "reference" and logic.strict_round_mode():
            return f"👁️ {page}"
        return page

    return label


def _sidebar_todo(team):
    """A compact 'what still needs doing this round' tracker in the sidebar."""
    rnd = db.current_round()
    cl = logic.round_checklist(team["id"], rnd)
    items = list(cl["decisions"]) + list(cl["questions"]) + list(cl["carried"])
    # Reading new Inbox mail is a to-do too (it carries this round's feedback/hints).
    unread = db.unread_count(team["id"])
    if unread:
        items.append({"label": f"Read {unread} new Inbox message(s)", "tool": "Inbox",
                      "done": False})
    # Any AI use still unverified is a to-do (verification is what earns credit).
    ai_unv = logic.ai_unverified_count(team["id"])
    if ai_unv:
        items.append({"label": f"Verify {ai_unv} AI use(s)", "tool": "AI Assist Log",
                      "done": False})
    if not items:
        return
    done = sum(1 for i in items if i["done"])
    total = len(items)
    st.progress(done / total if total else 1.0, text=f"Round {rnd} to-do: {done}/{total} done")
    nxt = logic.next_action(team["id"], rnd)
    if nxt:
        where = f" → {nxt['tool']}" if nxt.get("tool") else ""
        st.caption(f"👉 **Next:** {nxt['label']}{where}")
    open_items = [i for i in items if not i["done"]]
    if open_items:
        with st.expander(f"📝 {len(open_items)} still to do"):
            for i in open_items:
                tool = i.get("tool", "")
                carried = " ⏪" if i.get("carried") else ""
                label = i.get("label", i.get("concept", ""))
                st.caption(f"⬜ {label}" + (f" · *{tool}*" if tool else "") + carried)
    else:
        st.caption("✅ Everything for this round is done.")


def _sidebar_commit_status(team):
    """Commit/withdraw controls + deadline banner, always visible in the team sidebar."""
    rnd = db.current_round()
    state = logic.commitment_state(team["id"], rnd)
    ds = state["deadline"]

    if state["committed"]:
        if state["locked"]:
            st.success(f"✅ Round {rnd} committed · locked")
            st.caption("The deadline has passed — this round is final.")
        else:
            st.success(f"🔒 Round {rnd} committed — editing locked")
            if st.button("↩️ Withdraw to edit", use_container_width=True,
                         help="Unlock every tool so you can change your work. Re-commit when done."):
                ok, msg = logic.decommit_round(team["id"], rnd)
                st.rerun()
    else:
        if state["locked"]:
            st.error(f"🔒 Round {rnd} closed — not committed")
            st.caption("The deadline passed before you committed.")
        else:
            if ds["set"]:
                st.warning(f"⚠️ Round {rnd} not committed · due in {ds['remaining']}")
            else:
                st.warning(f"⚠️ Round {rnd} not committed")
            if st.button("✅ Commit round", type="primary", use_container_width=True,
                         help="Lock in this round's work for scoring. Every tool becomes "
                              "view-only until you withdraw."):
                ok, msg = logic.commit_round(team["id"], rnd)
                st.rerun()
            st.caption("Committing locks all tools. You can withdraw any time before the deadline.")


def student_shell():
    team = db.get_team(st.session_state.team_id)
    if not team:
        st.error("Team no longer exists.")
        logout()
        st.stop()
    # A student plays inside their team's game — advance that game, not others.
    db.set_active_game(team.get("game_id"))
    _sync_active_game()
    team = db.get_team(team["id"])   # round may have advanced

    # Celebrate any newly-earned badges.
    for code in logic.sync_badges(team["id"]):
        b = content.BADGE_BY_CODE.get(code, {})
        try:
            st.toast(f"🏅 Badge unlocked: {b.get('emoji','')} {b.get('name', code)}!")
        except Exception:
            pass

    ident = logic.team_identity(team)
    level, _ = logic.founder_level(team["id"])
    streak = logic.commit_streak(team["id"])
    n_badges = len(logic.team_badges(team["id"]))
    with st.sidebar:
        branding.sidebar_logo()
        st.markdown(branding.team_badge_html(team, 44), unsafe_allow_html=True)
        st.caption(f"Round {db.current_round()} · {team['stage']}  ·  "
                   f"🧑‍🚀 Lvl {level} · 🏅 {n_badges}"
                   + (f" · 🔥 {streak}-round streak" if streak >= 2 else ""))
        st.metric("Credits", f"{team['evidence_credits']:.1f}")
        _sidebar_todo(team)
        _sidebar_commit_status(team)
        page = st.radio("Go to", list(STUDENT_PAGES.keys()),
                        format_func=_make_student_label(team))
        st.caption("🔒 locked (opens later) · 👁️ reference-only this round · others are active. "
                   "Round Briefing ✅ = committed, ⚠️ = not yet.")
        with st.expander("Rotating team roles"):
            for role, desc in content.TEAM_ROLES:
                st.caption(f"**{role}** — {desc}")
        st.button("Log out", on_click=logout)

    _scroll_top_on_change("_student_page", page)
    STUDENT_PAGES[page](team)


# --------------------------------------------------------------------------- #
# Instructor shell
# --------------------------------------------------------------------------- #
INSTRUCTOR_PAGES = {
    "Games": vi.games_console,
    "Cohort Overview": vi.overview,
    "Auto-Director": vi.auto_director,
    "Team Setup": vi.team_setup,
    "Schedule & Timing": vi.schedule,
    "Round Control": vi.round_control,
    "Resources": vi.resources,
    "Market Events": vi.events,
    "VP Auction": vi.vp_auction,
    "Pivot Committee": vi.pivot_committee,
    "Dashboard Scoring": vi.scoring,
    "Round Scores": vi.round_scores,
    "Misconception Radar": vi.misconception_radar,
    "Demo Day": vi.demo_day_admin,
}


def instructor_shell():
    # Pick which game the Director is managing (each runs independently).
    games = db.list_games()
    if not games:
        db.create_game("Game 1")
        games = db.list_games()
    saved = st.session_state.get("active_game_id")
    ids = [g["id"] for g in games]
    if saved not in ids:
        saved = ids[0]
    with st.sidebar:
        branding.sidebar_logo()
        st.header("🎩 Venture Foundry Director")
        gsel = st.selectbox(
            "Active game", ids, index=ids.index(saved),
            format_func=lambda i: next(g["name"] for g in games if g["id"] == i),
            help="Manage one game at a time. Each game advances on its own round.")
        st.session_state["active_game_id"] = gsel
        db.set_active_game(gsel)
        _sync_active_game()
        diff = db.get_setting("difficulty", "not set")
        st.caption(f"Round {db.current_round()} of {logic.total_rounds()} · "
                   f"{len(db.list_teams())} team(s) · Difficulty: {diff}")
        page = st.radio("Console", list(INSTRUCTOR_PAGES.keys()))
        with st.expander("Director's questions"):
            for q in [
                "What must be true for this to work?",
                "Which assumption could invalidate the entire model?",
                "What evidence supports that claim?",
                "Is that evidence about intentions or behavior?",
                "What is the least expensive way to test it?",
                "What result would cause you to change direction?",
            ]:
                st.caption(f"• {q}")
        st.button("Log out", on_click=logout)

    _scroll_top_on_change("_instructor_page", page)
    INSTRUCTOR_PAGES[page]()


# --------------------------------------------------------------------------- #
# Router
# --------------------------------------------------------------------------- #
if st.session_state.role == "student":
    student_shell()
elif st.session_state.role == "instructor" and st.session_state.instructor_ok:
    instructor_shell()
else:
    landing()
