"""
db.py — SQLite persistence layer for Venture Foundry: The Evidence Economy.

A single-file database keeps the whole cohort's state so progress survives
restarts and multiple teams can play in parallel. All access goes through the
helpers here; views never write raw SQL.
"""

import sqlite3
import json
import os
import secrets
from datetime import datetime, timezone

DB_PATH = os.environ.get(
    "VF_DB_PATH",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "venture_foundry.db"),
)


# --------------------------------------------------------------------------- #
# Connection / bootstrap
# --------------------------------------------------------------------------- #
def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _dumps(obj):
    return json.dumps(obj, ensure_ascii=False)


def _loads(text, default=None):
    if not text:
        return default
    try:
        return json.loads(text)
    except (ValueError, TypeError):
        return default


SCHEMA = """
CREATE TABLE IF NOT EXISTS settings (
    key   TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE IF NOT EXISTS teams (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    name               TEXT NOT NULL,
    join_code          TEXT UNIQUE NOT NULL,
    opportunity        TEXT,
    founder_card       TEXT,            -- JSON
    ventures           TEXT,            -- JSON list of candidate ventures
    capital            REAL DEFAULT 0,
    evidence_credits   REAL DEFAULT 0,
    venture_tokens     INTEGER DEFAULT 100,
    founder_hours      REAL DEFAULT 0,
    stage              TEXT DEFAULT 'Opportunity formation',
    market_potential   REAL DEFAULT 1000000,
    unresolved_risk    REAL DEFAULT 0,
    created_at         TEXT
);

CREATE TABLE IF NOT EXISTS canvases (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id    INTEGER NOT NULL,
    ctype      TEXT NOT NULL,           -- customer_profile | vpc | bmc
    version    INTEGER NOT NULL,
    label      TEXT,
    data       TEXT,                    -- JSON block->text
    note       TEXT,
    created_at TEXT,
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS assumptions (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id        INTEGER NOT NULL,
    text           TEXT NOT NULL,
    risk_type      TEXT,                -- Desirability | Feasibility | Viability | Adaptability
    importance     INTEGER DEFAULT 3,   -- 1..5
    evidence_level INTEGER DEFAULT 1,   -- 1..5 (how much we already know)
    testability    INTEGER DEFAULT 3,   -- 1..5
    status         TEXT DEFAULT 'Untested',  -- Untested|Testing|Supported|Refuted|Ignored
    created_at     TEXT,
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS experiments (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id           INTEGER NOT NULL,
    assumption_id     INTEGER,
    card_type         TEXT,
    cost_money        REAL DEFAULT 0,
    cost_time         REAL DEFAULT 0,
    cost_credits      REAL DEFAULT 0,
    evidence_strength INTEGER DEFAULT 0,
    hypothesis        TEXT,
    metric            TEXT,
    success_threshold TEXT,
    failure_threshold TEXT,
    decision_rule     TEXT,
    result            TEXT,
    outcome           TEXT DEFAULT 'Designed',  -- Designed|Running|Supported|Refuted|Inconclusive
    created_at        TEXT,
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS evidence (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id       INTEGER NOT NULL,
    description   TEXT,
    evidence_type TEXT,
    strength      INTEGER DEFAULT 0,
    source        TEXT,
    assumption_id INTEGER,
    credits_award REAL DEFAULT 0,
    created_at    TEXT,
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS events (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id    INTEGER,                 -- NULL => broadcast to all teams
    round      INTEGER,
    category   TEXT,
    text       TEXT,
    exposes    TEXT,
    resolved   INTEGER DEFAULT 0,
    created_at TEXT,
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS pivots (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id          INTEGER NOT NULL,
    original_assum   TEXT,
    challenge_evid   TEXT,
    affected_block   TEXT,
    proposed_change  TEXT,
    change_cost      REAL DEFAULT 0,
    new_assumptions  TEXT,
    evidence_needed  TEXT,
    status           TEXT DEFAULT 'Submitted',  -- Submitted|Approved|Conditional|NeedsEvidence|Rejected|RandomChange
    committee_note   TEXT,
    created_at       TEXT,
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS reflections (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id      INTEGER NOT NULL,
    student_name TEXT,
    round        INTEGER,
    expected     TEXT,
    occurred     TEXT,
    assumption   TEXT,
    overlooked   TEXT,
    differently  TEXT,
    contribution TEXT,
    created_at   TEXT,
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS scores (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id    INTEGER NOT NULL,
    round      INTEGER,
    dimension  TEXT,
    score      REAL,                    -- 0..100
    created_at TEXT,
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS transactions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id     INTEGER NOT NULL,
    kind        TEXT,
    money       REAL DEFAULT 0,
    credits     REAL DEFAULT 0,
    hours       REAL DEFAULT 0,
    description TEXT,
    created_at  TEXT,
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS value_props (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id          INTEGER NOT NULL,
    name             TEXT NOT NULL,
    description      TEXT,
    evidence_strength INTEGER DEFAULT 0,   -- 0..10, should reflect the evidence ledger
    tokens           INTEGER DEFAULT 0,    -- current Venture Token allocation
    prev_tokens      INTEGER,              -- allocation at previous auction (NULL until first run)
    created_at       TEXT,
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS vp_results (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id        INTEGER NOT NULL,
    round          INTEGER,
    total_tokens   INTEGER,
    alignment      REAL,
    prev_alignment REAL,
    tax            REAL,
    dividend       REAL,
    net_credits    REAL,
    note           TEXT,
    created_at     TEXT,
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ai_logs (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id       INTEGER NOT NULL,
    round         INTEGER,
    tool_area     TEXT,
    prompt        TEXT,
    ai_output     TEXT,
    audit_a       TEXT,   -- Assumptions surfaced
    audit_u       TEXT,   -- Unsupported claims flagged
    audit_d       TEXT,   -- Data & sources checked
    audit_i       TEXT,   -- Independent test designed
    audit_t       TEXT,   -- Translate to evidence
    status        TEXT DEFAULT 'Unverified',
    created_at    TEXT,
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS schedule (
    round      INTEGER PRIMARY KEY,   -- 1..total_rounds
    topic_key  TEXT,                  -- references a curriculum topic key
    advance_at TEXT                   -- ISO datetime this round should begin (optional)
);
"""


def init_db():
    conn = get_conn()
    try:
        conn.executescript(SCHEMA)
        # Seed default settings once.
        cur = conn.execute("SELECT value FROM settings WHERE key='current_round'")
        if cur.fetchone() is None:
            conn.execute(
                "INSERT INTO settings(key, value) VALUES(?,?)",
                ("current_round", "1"),
            )
            conn.execute(
                "INSERT INTO settings(key, value) VALUES(?,?)",
                ("instructor_pin", "foundry"),
            )
        conn.commit()
    finally:
        conn.close()
    # Seed the default schedule/total-rounds on first run (import here to avoid a
    # circular import at module load).
    import content
    if get_setting("total_rounds") is None:
        set_setting("total_rounds", content.DEFAULT_TOTAL_ROUNDS)
    if not get_schedule_rows():
        for i, key in enumerate(content.DEFAULT_TOPIC_ORDER):
            upsert_schedule_row(i + 1, key, None)


# --------------------------------------------------------------------------- #
# Settings
# --------------------------------------------------------------------------- #
def get_setting(key, default=None):
    conn = get_conn()
    try:
        row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return row["value"] if row else default
    finally:
        conn.close()


def set_setting(key, value):
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO settings(key, value) VALUES(?,?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, str(value)),
        )
        conn.commit()
    finally:
        conn.close()


def current_round():
    return int(get_setting("current_round", "1"))


# --------------------------------------------------------------------------- #
# Teams
# --------------------------------------------------------------------------- #
def create_team(name, opportunity="", founder_card=None, capital=2000,
                evidence_credits=10, founder_hours=120, market_potential=1000000):
    conn = get_conn()
    try:
        code = secrets.token_hex(3).upper()
        conn.execute(
            """INSERT INTO teams(name, join_code, opportunity, founder_card, ventures,
                                 capital, evidence_credits, venture_tokens, founder_hours,
                                 market_potential, created_at)
               VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
            (name, code, opportunity, _dumps(founder_card or {}), _dumps([]),
             capital, evidence_credits, 100, founder_hours, market_potential, now()),
        )
        conn.commit()
        return code
    finally:
        conn.close()


def list_teams():
    conn = get_conn()
    try:
        rows = conn.execute("SELECT * FROM teams ORDER BY name").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_team(team_id):
    conn = get_conn()
    try:
        row = conn.execute("SELECT * FROM teams WHERE id=?", (team_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_team_by_code(code):
    conn = get_conn()
    try:
        row = conn.execute(
            "SELECT * FROM teams WHERE join_code=?", (code.strip().upper(),)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def update_team(team_id, **fields):
    if not fields:
        return
    conn = get_conn()
    try:
        cols = ", ".join(f"{k}=?" for k in fields)
        conn.execute(f"UPDATE teams SET {cols} WHERE id=?", (*fields.values(), team_id))
        conn.commit()
    finally:
        conn.close()


def delete_team(team_id):
    conn = get_conn()
    try:
        conn.execute("DELETE FROM teams WHERE id=?", (team_id,))
        conn.commit()
    finally:
        conn.close()


def set_ventures(team_id, ventures):
    update_team(team_id, ventures=_dumps(ventures))


def get_ventures(team_id):
    t = get_team(team_id)
    return _loads(t["ventures"], []) if t else []


def get_founder_card(team_id):
    t = get_team(team_id)
    return _loads(t["founder_card"], {}) if t else {}


# --------------------------------------------------------------------------- #
# Resource ledger — the ONLY path that changes money/credits/hours
# --------------------------------------------------------------------------- #
def adjust_resources(team_id, money=0, credits=0, hours=0, kind="adjust",
                     description="", allow_negative=False):
    """Apply a resource change and record a transaction.

    Returns (ok, message). If allow_negative is False and the change would push
    money/credits/hours below zero, nothing is written.
    """
    t = get_team(team_id)
    if not t:
        return False, "Team not found."
    new_money = t["capital"] + money
    new_credits = t["evidence_credits"] + credits
    new_hours = t["founder_hours"] + hours
    if not allow_negative:
        if new_money < 0:
            return False, "Not enough capital."
        if new_credits < 0:
            return False, "Not enough Evidence Credits."
        if new_hours < 0:
            return False, "Not enough founder-hours."
    conn = get_conn()
    try:
        conn.execute(
            "UPDATE teams SET capital=?, evidence_credits=?, founder_hours=? WHERE id=?",
            (new_money, new_credits, new_hours, team_id),
        )
        conn.execute(
            """INSERT INTO transactions(team_id, kind, money, credits, hours, description, created_at)
               VALUES(?,?,?,?,?,?,?)""",
            (team_id, kind, money, credits, hours, description, now()),
        )
        conn.commit()
        return True, "OK"
    finally:
        conn.close()


def list_transactions(team_id, limit=100):
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT * FROM transactions WHERE team_id=? ORDER BY id DESC LIMIT ?",
            (team_id, limit),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# --------------------------------------------------------------------------- #
# Canvases (versioned)
# --------------------------------------------------------------------------- #
def next_version(team_id, ctype):
    conn = get_conn()
    try:
        row = conn.execute(
            "SELECT MAX(version) AS m FROM canvases WHERE team_id=? AND ctype=?",
            (team_id, ctype),
        ).fetchone()
        return (row["m"] or 0) + 1
    finally:
        conn.close()


def save_canvas(team_id, ctype, data, label="", note=""):
    v = next_version(team_id, ctype)
    conn = get_conn()
    try:
        conn.execute(
            """INSERT INTO canvases(team_id, ctype, version, label, data, note, created_at)
               VALUES(?,?,?,?,?,?,?)""",
            (team_id, ctype, v, label, _dumps(data), note, now()),
        )
        conn.commit()
        return v
    finally:
        conn.close()


def list_canvases(team_id, ctype=None):
    conn = get_conn()
    try:
        if ctype:
            rows = conn.execute(
                "SELECT * FROM canvases WHERE team_id=? AND ctype=? ORDER BY version",
                (team_id, ctype),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM canvases WHERE team_id=? ORDER BY ctype, version",
                (team_id,),
            ).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            d["data"] = _loads(d["data"], {})
            out.append(d)
        return out
    finally:
        conn.close()


def latest_canvas(team_id, ctype):
    cs = list_canvases(team_id, ctype)
    return cs[-1] if cs else None


# --------------------------------------------------------------------------- #
# Assumptions
# --------------------------------------------------------------------------- #
def add_assumption(team_id, text, risk_type="Desirability", importance=3,
                   evidence_level=1, testability=3):
    conn = get_conn()
    try:
        conn.execute(
            """INSERT INTO assumptions(team_id, text, risk_type, importance,
                                       evidence_level, testability, status, created_at)
               VALUES(?,?,?,?,?,?, 'Untested', ?)""",
            (team_id, text, risk_type, importance, evidence_level, testability, now()),
        )
        conn.commit()
    finally:
        conn.close()


def list_assumptions(team_id):
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT * FROM assumptions WHERE team_id=? ORDER BY importance DESC, id",
            (team_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def update_assumption(assum_id, **fields):
    if not fields:
        return
    conn = get_conn()
    try:
        cols = ", ".join(f"{k}=?" for k in fields)
        conn.execute(f"UPDATE assumptions SET {cols} WHERE id=?",
                     (*fields.values(), assum_id))
        conn.commit()
    finally:
        conn.close()


def delete_assumption(assum_id):
    conn = get_conn()
    try:
        conn.execute("DELETE FROM assumptions WHERE id=?", (assum_id,))
        conn.commit()
    finally:
        conn.close()


# --------------------------------------------------------------------------- #
# Experiments
# --------------------------------------------------------------------------- #
def add_experiment(team_id, assumption_id, card_type, cost_money, cost_time,
                   cost_credits, evidence_strength, hypothesis, metric,
                   success_threshold, failure_threshold, decision_rule):
    conn = get_conn()
    try:
        cur = conn.execute(
            """INSERT INTO experiments(team_id, assumption_id, card_type, cost_money,
                cost_time, cost_credits, evidence_strength, hypothesis, metric,
                success_threshold, failure_threshold, decision_rule, outcome, created_at)
               VALUES(?,?,?,?,?,?,?,?,?,?,?,?, 'Designed', ?)""",
            (team_id, assumption_id, card_type, cost_money, cost_time, cost_credits,
             evidence_strength, hypothesis, metric, success_threshold,
             failure_threshold, decision_rule, now()),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def list_experiments(team_id):
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT * FROM experiments WHERE team_id=? ORDER BY id DESC", (team_id,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def update_experiment(exp_id, **fields):
    if not fields:
        return
    conn = get_conn()
    try:
        cols = ", ".join(f"{k}=?" for k in fields)
        conn.execute(f"UPDATE experiments SET {cols} WHERE id=?",
                     (*fields.values(), exp_id))
        conn.commit()
    finally:
        conn.close()


# --------------------------------------------------------------------------- #
# Evidence ledger
# --------------------------------------------------------------------------- #
def add_evidence(team_id, description, evidence_type, strength, source,
                 assumption_id=None, credits_award=0):
    conn = get_conn()
    try:
        conn.execute(
            """INSERT INTO evidence(team_id, description, evidence_type, strength,
                                    source, assumption_id, credits_award, created_at)
               VALUES(?,?,?,?,?,?,?,?)""",
            (team_id, description, evidence_type, strength, source,
             assumption_id, credits_award, now()),
        )
        conn.commit()
    finally:
        conn.close()


def list_evidence(team_id):
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT * FROM evidence WHERE team_id=? ORDER BY id DESC", (team_id,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# --------------------------------------------------------------------------- #
# Market events
# --------------------------------------------------------------------------- #
def add_event(team_id, round_no, category, text, exposes=""):
    conn = get_conn()
    try:
        conn.execute(
            """INSERT INTO events(team_id, round, category, text, exposes, resolved, created_at)
               VALUES(?,?,?,?,?,0,?)""",
            (team_id, round_no, category, text, exposes, now()),
        )
        conn.commit()
    finally:
        conn.close()


def list_events(team_id=None, include_broadcast=True):
    conn = get_conn()
    try:
        if team_id is None:
            rows = conn.execute("SELECT * FROM events ORDER BY id DESC").fetchall()
        elif include_broadcast:
            rows = conn.execute(
                "SELECT * FROM events WHERE team_id=? OR team_id IS NULL ORDER BY id DESC",
                (team_id,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM events WHERE team_id=? ORDER BY id DESC", (team_id,)
            ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def resolve_event(event_id, resolved=1):
    conn = get_conn()
    try:
        conn.execute("UPDATE events SET resolved=? WHERE id=?", (resolved, event_id))
        conn.commit()
    finally:
        conn.close()


# --------------------------------------------------------------------------- #
# Pivot petitions
# --------------------------------------------------------------------------- #
def add_pivot(team_id, data):
    conn = get_conn()
    try:
        conn.execute(
            """INSERT INTO pivots(team_id, original_assum, challenge_evid, affected_block,
                proposed_change, change_cost, new_assumptions, evidence_needed,
                status, created_at)
               VALUES(?,?,?,?,?,?,?,?, 'Submitted', ?)""",
            (team_id, data.get("original_assum", ""), data.get("challenge_evid", ""),
             data.get("affected_block", ""), data.get("proposed_change", ""),
             data.get("change_cost", 0), data.get("new_assumptions", ""),
             data.get("evidence_needed", ""), now()),
        )
        conn.commit()
    finally:
        conn.close()


def list_pivots(team_id=None):
    conn = get_conn()
    try:
        if team_id is None:
            rows = conn.execute("SELECT * FROM pivots ORDER BY id DESC").fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM pivots WHERE team_id=? ORDER BY id DESC", (team_id,)
            ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def decide_pivot(pivot_id, status, note=""):
    conn = get_conn()
    try:
        conn.execute("UPDATE pivots SET status=?, committee_note=? WHERE id=?",
                     (status, note, pivot_id))
        conn.commit()
    finally:
        conn.close()


# --------------------------------------------------------------------------- #
# Reflections
# --------------------------------------------------------------------------- #
def add_reflection(team_id, data):
    conn = get_conn()
    try:
        conn.execute(
            """INSERT INTO reflections(team_id, student_name, round, expected, occurred,
                assumption, overlooked, differently, contribution, created_at)
               VALUES(?,?,?,?,?,?,?,?,?,?)""",
            (team_id, data.get("student_name", ""), data.get("round", 1),
             data.get("expected", ""), data.get("occurred", ""),
             data.get("assumption", ""), data.get("overlooked", ""),
             data.get("differently", ""), data.get("contribution", ""), now()),
        )
        conn.commit()
    finally:
        conn.close()


def list_reflections(team_id=None):
    conn = get_conn()
    try:
        if team_id is None:
            rows = conn.execute("SELECT * FROM reflections ORDER BY id DESC").fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM reflections WHERE team_id=? ORDER BY id DESC", (team_id,)
            ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# --------------------------------------------------------------------------- #
# Dashboard scores
# --------------------------------------------------------------------------- #
def set_score(team_id, round_no, dimension, score):
    conn = get_conn()
    try:
        conn.execute(
            """INSERT INTO scores(team_id, round, dimension, score, created_at)
               VALUES(?,?,?,?,?)""",
            (team_id, round_no, dimension, score, now()),
        )
        conn.commit()
    finally:
        conn.close()


def latest_scores(team_id):
    """Return {dimension: score} using the most recent entry per dimension."""
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT dimension, score FROM scores WHERE team_id=? "
            "ORDER BY id ASC", (team_id,)
        ).fetchall()
        out = {}
        for r in rows:
            out[r["dimension"]] = r["score"]
        return out
    finally:
        conn.close()


# --------------------------------------------------------------------------- #
# Value Proposition Auction
# --------------------------------------------------------------------------- #
def add_value_prop(team_id, name, description="", evidence_strength=0):
    conn = get_conn()
    try:
        conn.execute(
            """INSERT INTO value_props(team_id, name, description, evidence_strength,
                                       tokens, prev_tokens, created_at)
               VALUES(?,?,?,?,0,NULL,?)""",
            (team_id, name, description, evidence_strength, now()),
        )
        conn.commit()
    finally:
        conn.close()


def list_value_props(team_id):
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT * FROM value_props WHERE team_id=? ORDER BY id", (team_id,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def update_value_prop(vp_id, **fields):
    if not fields:
        return
    conn = get_conn()
    try:
        cols = ", ".join(f"{k}=?" for k in fields)
        conn.execute(f"UPDATE value_props SET {cols} WHERE id=?",
                     (*fields.values(), vp_id))
        conn.commit()
    finally:
        conn.close()


def delete_value_prop(vp_id):
    conn = get_conn()
    try:
        conn.execute("DELETE FROM value_props WHERE id=?", (vp_id,))
        conn.commit()
    finally:
        conn.close()


def record_vp_result(team_id, round_no, total_tokens, alignment, prev_alignment,
                     tax, dividend, net_credits, note=""):
    conn = get_conn()
    try:
        conn.execute(
            """INSERT INTO vp_results(team_id, round, total_tokens, alignment,
                prev_alignment, tax, dividend, net_credits, note, created_at)
               VALUES(?,?,?,?,?,?,?,?,?,?)""",
            (team_id, round_no, total_tokens, alignment, prev_alignment, tax,
             dividend, net_credits, note, now()),
        )
        conn.commit()
    finally:
        conn.close()


def list_vp_results(team_id=None):
    conn = get_conn()
    try:
        if team_id is None:
            rows = conn.execute("SELECT * FROM vp_results ORDER BY id DESC").fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM vp_results WHERE team_id=? ORDER BY id DESC", (team_id,)
            ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# --------------------------------------------------------------------------- #
# Generative-AI assist logs (AUDIT verification)
# --------------------------------------------------------------------------- #
def add_ai_log(team_id, data):
    conn = get_conn()
    try:
        conn.execute(
            """INSERT INTO ai_logs(team_id, round, tool_area, prompt, ai_output,
                audit_a, audit_u, audit_d, audit_i, audit_t, status, created_at)
               VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
            (team_id, data.get("round", 1), data.get("tool_area", ""),
             data.get("prompt", ""), data.get("ai_output", ""),
             data.get("audit_a", ""), data.get("audit_u", ""), data.get("audit_d", ""),
             data.get("audit_i", ""), data.get("audit_t", ""),
             data.get("status", "Unverified"), now()),
        )
        conn.commit()
    finally:
        conn.close()


def list_ai_logs(team_id=None):
    conn = get_conn()
    try:
        if team_id is None:
            rows = conn.execute("SELECT * FROM ai_logs ORDER BY id DESC").fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM ai_logs WHERE team_id=? ORDER BY id DESC", (team_id,)
            ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def update_ai_log(log_id, **fields):
    if not fields:
        return
    conn = get_conn()
    try:
        cols = ", ".join(f"{k}=?" for k in fields)
        conn.execute(f"UPDATE ai_logs SET {cols} WHERE id=?", (*fields.values(), log_id))
        conn.commit()
    finally:
        conn.close()


def delete_ai_log(log_id):
    conn = get_conn()
    try:
        conn.execute("DELETE FROM ai_logs WHERE id=?", (log_id,))
        conn.commit()
    finally:
        conn.close()


# --------------------------------------------------------------------------- #
# Schedule (round -> topic -> advance datetime). Raw CRUD; higher-level seeding
# and derived queries live in logic.py.
# --------------------------------------------------------------------------- #
def get_schedule_rows():
    conn = get_conn()
    try:
        rows = conn.execute("SELECT * FROM schedule ORDER BY round").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def upsert_schedule_row(round_no, topic_key, advance_at=None):
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO schedule(round, topic_key, advance_at) VALUES(?,?,?) "
            "ON CONFLICT(round) DO UPDATE SET topic_key=excluded.topic_key, "
            "advance_at=excluded.advance_at",
            (round_no, topic_key, advance_at),
        )
        conn.commit()
    finally:
        conn.close()


def set_schedule_topic(round_no, topic_key):
    conn = get_conn()
    try:
        conn.execute("UPDATE schedule SET topic_key=? WHERE round=?", (topic_key, round_no))
        conn.commit()
    finally:
        conn.close()


def set_schedule_advance(round_no, advance_at):
    conn = get_conn()
    try:
        conn.execute("UPDATE schedule SET advance_at=? WHERE round=?", (advance_at, round_no))
        conn.commit()
    finally:
        conn.close()


def delete_schedule_rows_above(max_round):
    conn = get_conn()
    try:
        conn.execute("DELETE FROM schedule WHERE round > ?", (max_round,))
        conn.commit()
    finally:
        conn.close()
