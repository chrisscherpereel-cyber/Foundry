"""
Venture Foundry — The Evidence Economy
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

import streamlit as st
import streamlit.components.v1 as components

import db
import content
import logic
import branding
import views_student as vs
import views_instructor as vi

st.set_page_config(page_title="Venture Foundry — The Evidence Economy",
                   page_icon="🏭", layout="wide")

db.init_db()
# Date/time-based round advance, applied on load. If the round moved forward and
# the Director enabled it, run the Auto-Director for the new round.
_prev_round = db.current_round()
_new_round = logic.maybe_auto_advance()
if _new_round != _prev_round and logic.auto_flag("auto_run_on_advance", default=False):
    logic.run_autopilot(_new_round)


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
    "Concept Check": vs.concept_check,
    "Dashboard": vs.dashboard,
    "Founder & Opportunity": vs.founder_opportunity,
    "Founder Skills": vs.founder_skills,
    "Canvases": vs.canvases,
    "VP Auction": vs.vp_auction,
    "Assumption Map": vs.assumptions,
    "Experiment Marketplace": vs.experiments,
    "Evidence Ledger": vs.evidence,
    "Market Events": vs.market_events,
    "Pivot Petition": vs.pivots,
    "AI Assist Log": vs.ai_assist,
    "Decision Journal": vs.reflections,
}


def _make_student_label(team):
    """Sidebar labels: lock/reference state + round tag + Inbox unread badge."""
    unread = db.unread_count(team["id"])
    rnd = db.current_round()

    def label(page):
        if page == "Inbox":
            return f"Inbox 🔵{unread}" if unread else "Inbox"
        state = logic.tool_state(page, rnd, team["id"])
        if state == "locked":
            return f"🔒 {page} · R{logic.page_unlock_round(page)}"
        if state == "reference" and logic.strict_round_mode():
            return f"👁️ {page}"
        return page

    return label


def student_shell():
    team = db.get_team(st.session_state.team_id)
    if not team:
        st.error("Team no longer exists.")
        logout()
        st.stop()

    with st.sidebar:
        branding.sidebar_logo()
        st.header(f"🎓 {team['name']}")
        st.caption(f"Round {db.current_round()} · {team['stage']}")
        st.metric("Credits", f"{team['evidence_credits']:.1f}")
        page = st.radio("Go to", list(STUDENT_PAGES.keys()),
                        format_func=_make_student_label(team))
        st.caption("🔒 locked (opens later) · 👁️ reference-only this round · others are active.")
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
}


def instructor_shell():
    with st.sidebar:
        branding.sidebar_logo()
        st.header("🎩 Venture Foundry Director")
        diff = db.get_setting("difficulty", "not set")
        st.caption(f"Round {db.current_round()} of {logic.total_rounds()} · Difficulty: {diff}")
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
