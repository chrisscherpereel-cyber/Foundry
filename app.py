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

import db
import content
import views_student as vs
import views_instructor as vi

st.set_page_config(page_title="Venture Foundry — The Evidence Economy",
                   page_icon="🏭", layout="wide")

db.init_db()

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
    st.title("🏭 Venture Foundry — The Evidence Economy")
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
    "Dashboard": vs.dashboard,
    "Founder & Opportunity": vs.founder_opportunity,
    "Canvases": vs.canvases,
    "VP Auction": vs.vp_auction,
    "Assumption Map": vs.assumptions,
    "Experiment Marketplace": vs.experiments,
    "Evidence Ledger": vs.evidence,
    "Market Events": vs.market_events,
    "Pivot Petition": vs.pivots,
    "Decision Journal": vs.reflections,
}


def student_shell():
    team = db.get_team(st.session_state.team_id)
    if not team:
        st.error("Team no longer exists.")
        logout()
        st.stop()

    with st.sidebar:
        st.header(f"🎓 {team['name']}")
        st.caption(f"Round {db.current_round()} · {team['stage']}")
        st.metric("Credits", f"{team['evidence_credits']:.1f}")
        page = st.radio("Go to", list(STUDENT_PAGES.keys()))
        with st.expander("Rotating team roles"):
            for role, desc in content.TEAM_ROLES:
                st.caption(f"**{role}** — {desc}")
        st.button("Log out", on_click=logout)

    STUDENT_PAGES[page](team)


# --------------------------------------------------------------------------- #
# Instructor shell
# --------------------------------------------------------------------------- #
INSTRUCTOR_PAGES = {
    "Cohort Overview": vi.overview,
    "Team Setup": vi.team_setup,
    "Round Control": vi.round_control,
    "Resources": vi.resources,
    "Market Events": vi.events,
    "VP Auction": vi.vp_auction,
    "Pivot Committee": vi.pivot_committee,
    "Dashboard Scoring": vi.scoring,
}


def instructor_shell():
    with st.sidebar:
        st.header("🎩 Venture Foundry Director")
        st.caption(f"Round {db.current_round()}")
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
