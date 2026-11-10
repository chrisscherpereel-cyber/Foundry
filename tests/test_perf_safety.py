"""Regression tests for the performance/concurrency changes.

Run:  pip install pytest && pytest -q tests/
Each test uses a throwaway SQLite file, never venture_foundry.db.
"""
import os
import sys
import tempfile
import threading
from datetime import datetime, timedelta, timezone

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
_TMP = tempfile.mkdtemp()
os.environ["VF_DB_PATH"] = os.path.join(_TMP, "test.db")

import db      # noqa: E402
import logic   # noqa: E402


@pytest.fixture(autouse=True)
def fresh_db():
    for suffix in ("", "-wal", "-shm"):
        p = db.DB_PATH + suffix
        if os.path.exists(p):
            os.remove(p)
    db.end_request()
    db.init_db()
    gid = db.list_games()[0]["id"]
    db.set_active_game(gid)
    yield gid
    db.end_request()


def _team(credits=10):
    code = db.create_team("T", evidence_credits=credits)
    return db.get_team_by_code(code)["id"]


# ---- per-run read cache ---------------------------------------------------- #
def test_wal_enabled():
    conn = db.get_conn()
    try:
        assert conn.execute("PRAGMA journal_mode").fetchone()[0].lower() == "wal"
    finally:
        conn.close()


def test_no_caching_outside_a_run():
    db.set_setting("k", "1")
    assert db.get_setting("k") == "1"
    conn = db.get_conn()            # raw write that bypasses helpers, no commit hook
    conn.execute("UPDATE settings SET value='2' WHERE key='k'")
    sqlite3_commit = super(type(conn), conn).commit
    sqlite3_commit()
    conn.close()
    assert db.get_setting("k") == "2"


def test_cache_hits_within_run_and_clears_on_write():
    db.set_setting("k", "1")
    db.begin_request()
    assert db.get_setting("k") == "1"
    # A write by another connection that doesn't go through our commit hook is not
    # seen within the same run (snapshot semantics) ...
    conn = db.get_conn()
    conn.execute("UPDATE settings SET value='2' WHERE key='k'")
    super(type(conn), conn).commit()
    conn.close()
    assert db.get_setting("k") == "1"
    # ... but any helper write clears the cache.
    db.set_setting("other", "x")
    assert db.get_setting("k") == "2"
    db.end_request()


def test_cached_results_are_copies():
    tid = _team()
    db.begin_request()
    t = db.get_team(tid)
    t["name"] = "MUTATED"
    assert db.get_team(tid)["name"] == "T"
    rows = logic.get_schedule()
    rows[0]["topics"].clear()
    assert logic.get_schedule()[0]["topics"] is not rows[0]["topics"]
    db.end_request()


def test_checklist_identical_with_and_without_cache():
    tid = _team()
    rnd = db.current_round()
    plain = logic.round_checklist(tid, rnd)
    db.begin_request()
    cached1 = logic.round_checklist(tid, rnd)
    cached2 = logic.round_checklist(tid, rnd)
    db.end_request()
    assert plain == cached1 == cached2


# ---- atomic resource updates ------------------------------------------------ #
def test_concurrent_spending_never_overdraws():
    tid = _team(credits=10)
    results = []

    def spend():
        results.append(db.adjust_resources(tid, credits=-1)[0])

    threads = [threading.Thread(target=spend) for _ in range(25)]
    [t.start() for t in threads]
    [t.join() for t in threads]
    assert results.count(True) == 10
    assert db.get_team(tid)["evidence_credits"] == 0
    assert len([x for x in db.list_transactions(tid) if x["credits"] == -1]) == 10


def test_increment_team_field_is_atomic():
    tid = _team()
    threads = [threading.Thread(target=db.increment_team_field, args=(tid, "spent_build", 1))
               for _ in range(30)]
    [t.start() for t in threads]
    [t.join() for t in threads]
    assert db.get_team(tid)["spent_build"] == 30
    with pytest.raises(ValueError):
        db.increment_team_field(tid, "capital", 1)


# ---- serialized round advance ---------------------------------------------- #
def test_simultaneous_loads_advance_round_once(fresh_db):
    gid = fresh_db
    tid = _team()
    db.add_hire(tid, "sales", "Rep", "part-time", 1, 100)
    start_capital = db.get_team(tid)["capital"]
    past = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
    db.set_schedule_advance(2, past)

    barrier = threading.Barrier(12)

    def load():
        db.set_active_game(gid)
        db.begin_request()
        barrier.wait()
        try:
            logic.sync_active_game()
        finally:
            db.end_request()

    threads = [threading.Thread(target=load) for _ in range(12)]
    [t.start() for t in threads]
    [t.join() for t in threads]
    db.set_active_game(gid)
    assert db.current_round() == 2
    # Exactly one round's salary charged, not one per simultaneous session.
    assert db.get_team(tid)["capital"] == start_capital - 100
