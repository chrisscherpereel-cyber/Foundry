"""
logic.py — Shared game logic: valuation, evidence economy, dashboard aggregation,
and the editable schedule (round -> topic -> advance time).

Kept free of Streamlit so it can be unit-tested and reused.
"""

from datetime import datetime, timezone

import db
import content


# --------------------------------------------------------------------------- #
# Schedule: number of rounds, topic per round, advance datetimes, auto-advance
# --------------------------------------------------------------------------- #
def total_rounds():
    try:
        return int(db.get_setting("total_rounds", content.DEFAULT_TOTAL_ROUNDS))
    except (TypeError, ValueError):
        return content.DEFAULT_TOTAL_ROUNDS


def get_schedule():
    """Return the ordered schedule: each round with its LIST of topic dicts.

    A round may cover several pieces of material, which lets a full 15-topic
    curriculum be compressed into fewer rounds.
    """
    placements = db.get_round_topics()          # ordered by round, position
    adv = {r["round"]: r["advance_at"] for r in db.get_schedule_rows()}
    by_round = {}
    for p in placements:
        by_round.setdefault(p["round"], []).append(p["topic_key"])
    out = []
    n = total_rounds()
    for rnd in range(1, n + 1):
        keys = by_round.get(rnd, [])
        topics = [content.CURRICULUM_BY_KEY[k] for k in keys if k in content.CURRICULUM_BY_KEY]
        out.append({"round": rnd, "topics": topics, "advance_at": adv.get(rnd)})
    return out


def unassigned_topics():
    """Curriculum topics not placed in any round within range (the 'pool')."""
    n = total_rounds()
    placed = {p["topic_key"] for p in db.get_round_topics() if p["round"] and p["round"] <= n}
    return [t for t in content.CURRICULUM_TOPICS if t["key"] not in placed]


def set_total_rounds(n):
    """Change how many rounds the simulation runs.

    Growing adds empty rounds. Shrinking moves any material from removed rounds
    onto the last remaining round, so no topic is ever lost. Never lets
    current_round exceed the new max.
    """
    n = max(1, int(n))
    # Move orphaned material (round > n) onto the last round.
    for p in db.get_round_topics():
        if p["round"] and p["round"] > n:
            db.set_topic_placement(p["topic_key"], n)
    # Ensure advance-time rows exist for each round; drop extras.
    existing = {r["round"] for r in db.get_schedule_rows()}
    for rnd in range(1, n + 1):
        if rnd not in existing:
            db.upsert_schedule_row(rnd, None, None)
    db.delete_schedule_rows_above(n)
    db.set_setting("total_rounds", n)
    if db.current_round() > n:
        db.set_setting("current_round", n)


def topics_for_round(rnd):
    """The list of curriculum topics covered in a given round."""
    for row in get_schedule():
        if row["round"] == rnd:
            return row["topics"]
    return []


def newly_unlocked(rnd):
    """Student tools first introduced at this round, across all its topics."""
    intro = []
    for topic in topics_for_round(rnd):
        for p in topic.get("introduces", []):
            if p not in intro:
                intro.append(p)
    if rnd == 1:
        intro = content.BASE_TOOLS + [p for p in intro if p not in content.BASE_TOOLS]
    return intro


def page_unlock_round(page):
    """Earliest round that introduces a page (1 for base tools / unscheduled)."""
    if page in content.BASE_TOOLS:
        return 1
    for row in get_schedule():
        for topic in row["topics"]:
            if page in topic.get("introduces", []):
                return row["round"]
    return 1  # never explicitly scheduled => always available


def canvas_unlock_round(canvas_type):
    """Earliest round whose material focuses on a given canvas type."""
    for row in get_schedule():
        for topic in row["topics"]:
            if topic.get("canvas") == canvas_type:
                return row["round"]
    return 1


def canvas_focus_for_round(rnd):
    """List of canvas types in focus this round (a round may cover several)."""
    focuses = []
    for topic in topics_for_round(rnd):
        c = topic.get("canvas")
        if c and c not in focuses:
            focuses.append(c)
    return focuses


def _parse_dt(text):
    if not text:
        return None
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def maybe_auto_advance():
    """Advance the current round if a scheduled advance time has passed.

    The app has no background scheduler, so this runs on page load: current_round
    becomes the highest round whose advance_at is in the past (never going backward,
    never exceeding total_rounds). Returns the (possibly unchanged) current round.
    """
    now = datetime.now(timezone.utc)
    cur = db.current_round()
    target = cur
    for row in get_schedule():
        dt = _parse_dt(row["advance_at"])
        if dt is not None:
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            if dt <= now and row["round"] > target:
                target = row["round"]
    if target != cur:
        db.set_setting("current_round", target)
    return target


def next_scheduled_advance():
    """Return (round, datetime_text) for the next future advance, or None."""
    now = datetime.now(timezone.utc)
    for row in get_schedule():
        dt = _parse_dt(row["advance_at"])
        if dt is not None:
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            if dt > now:
                return row["round"], row["advance_at"]
    return None


# --------------------------------------------------------------------------- #
# Evidence economy
# --------------------------------------------------------------------------- #
def credits_for_evidence(strength):
    """Evidence Credits earned for a logged piece of evidence of a given strength."""
    return round(strength * content.CREDITS_PER_STRENGTH, 1)


def log_evidence_and_award(team_id, description, evidence_type, source,
                           assumption_id=None):
    """Add evidence to the ledger and pay Evidence Credits for it.

    Behavioral evidence is worth more, so credits scale with ladder strength.
    Returns (credits_awarded, strength).
    """
    strength = content.EVIDENCE_LADDER_MAP.get(evidence_type, 0)
    award = credits_for_evidence(strength)
    db.add_evidence(team_id, description, evidence_type, strength, source,
                    assumption_id, award)
    if award > 0:
        db.adjust_resources(
            team_id, credits=award, kind="evidence",
            description=f"Evidence logged: {evidence_type}", allow_negative=True,
        )
    return award, strength


# --------------------------------------------------------------------------- #
# Experiment purchasing
# --------------------------------------------------------------------------- #
def purchase_experiment(team_id, card, assumption_id, hypothesis, metric,
                        success_threshold, failure_threshold, decision_rule):
    """Charge the team and record a designed experiment.

    Returns (ok, message, experiment_id|None).
    """
    ok, msg = db.adjust_resources(
        team_id,
        money=-card["money"],
        credits=-card["credits"],
        hours=-card["hours"],
        kind="experiment",
        description=f"Purchased experiment: {card['name']}",
    )
    if not ok:
        return False, msg, None
    exp_id = db.add_experiment(
        team_id, assumption_id, card["name"], card["money"], card["hours"],
        card["credits"], card["strength"], hypothesis, metric,
        success_threshold, failure_threshold, decision_rule,
    )
    return True, "Experiment purchased and designed.", exp_id


# --------------------------------------------------------------------------- #
# Valuation
#   Venture Value = Market Potential x Evidence Confidence x BM Coherence
#                   x Execution Factor - Unresolved Risk
#   Each index runs 0.50–1.50 and is derived from dashboard scores (0–100).
# --------------------------------------------------------------------------- #
def _index_from_score(score, default=0.90):
    """Map a 0–100 dashboard score onto a 0.50–1.50 index."""
    if score is None:
        return default
    return round(0.50 + (max(0.0, min(100.0, score)) / 100.0), 3)


def compute_valuation(team_id):
    """Return a dict with the valuation and its components."""
    team = db.get_team(team_id)
    if not team:
        return None
    scores = db.latest_scores(team_id)

    market_potential = team["market_potential"] or 0
    evidence_conf = _index_from_score(scores.get("Evidence Strength"))
    bm_coherence = _index_from_score(scores.get("Business-Model Coherence"))
    execution = _index_from_score(scores.get("Team Execution"))
    unresolved_risk = team["unresolved_risk"] or 0

    value = (market_potential * evidence_conf * bm_coherence * execution
             - unresolved_risk)
    return {
        "market_potential": market_potential,
        "evidence_confidence": evidence_conf,
        "bm_coherence": bm_coherence,
        "execution_factor": execution,
        "unresolved_risk": unresolved_risk,
        "valuation": round(value, 0),
    }


# --------------------------------------------------------------------------- #
# Evidence-portfolio analytics
# --------------------------------------------------------------------------- #
def evidence_summary(team_id):
    ev = db.list_evidence(team_id)
    total_strength = sum(e["strength"] for e in ev)
    total_credits = sum(e["credits_award"] for e in ev)
    behavioral = sum(1 for e in ev if e["strength"] >= 6)
    opinion = sum(1 for e in ev if e["strength"] <= 2)
    return {
        "count": len(ev),
        "total_strength": total_strength,
        "total_credits": round(total_credits, 1),
        "behavioral": behavioral,
        "opinion": opinion,
        "avg_strength": round(total_strength / len(ev), 1) if ev else 0,
    }


def assumption_risk_report(team_id):
    """Flag high-importance untested assumptions — the ones that can kill a venture."""
    assums = db.list_assumptions(team_id)
    exposed = [a for a in assums
               if a["importance"] >= 4 and a["status"] in ("Untested", "Ignored")]
    return {
        "total": len(assums),
        "untested": sum(1 for a in assums if a["status"] == "Untested"),
        "supported": sum(1 for a in assums if a["status"] == "Supported"),
        "refuted": sum(1 for a in assums if a["status"] == "Refuted"),
        "exposed": exposed,
    }


def quick_setup_teams(n_teams, difficulty, opportunity_mode="distinct",
                      opportunity_choice=None, founder_mode="balanced",
                      name_prefix="Team", clear_existing=False):
    """Create a balanced cohort of teams in one step.

    Every team receives IDENTICAL starting resources and market potential (from the
    chosen difficulty preset), which is what equalizes their odds of success. Only
    flavor differs by option:
      opportunity_mode : "same"     -> all teams get opportunity_choice
                         "distinct" -> rotate distinct territories (still balanced)
      founder_mode     : "balanced" -> everyone gets the neutral balanced card
                         "varied"   -> rotate founder archetypes, but resources are
                                       still forced equal so no one is advantaged

    Returns a list of {name, code, territory} for the teams created.
    """
    preset = content.DIFFICULTY_LEVELS.get(difficulty, content.DIFFICULTY_LEVELS["Standard"])
    if clear_existing:
        for t in db.list_teams():
            db.delete_team(t["id"])
    db.set_setting("difficulty", difficulty)

    territories = content.OPPORTUNITY_TERRITORIES
    if opportunity_mode == "same" and not opportunity_choice:
        opportunity_choice = territories[0]

    created = []
    for i in range(int(n_teams)):
        territory = (opportunity_choice if opportunity_mode == "same"
                     else territories[i % len(territories)])
        if founder_mode == "varied":
            base_card = dict(content.FOUNDER_CARDS[i % len(content.FOUNDER_CARDS)])
        else:
            base_card = dict(content.BALANCED_FOUNDER_CARD)
        # Force equal resources regardless of the card's own defaults => fair start.
        base_card["budget"] = preset["capital"]
        base_card["hours"] = preset["hours"]

        name = f"{name_prefix} {i + 1}"
        code = db.create_team(
            name, territory, base_card,
            capital=preset["capital"], evidence_credits=preset["credits"],
            founder_hours=preset["hours"], market_potential=preset["market_potential"],
        )
        created.append({"name": name, "code": code, "territory": territory})
    return created


def cohort_balance(team_list):
    """Report how equal the teams' starting resources are (fairness check).

    Returns a dict with the spread of capital, credits, hours, and market potential.
    A spread of 0 means a perfectly balanced cohort.
    """
    if not team_list:
        return None

    def spread(key):
        vals = [t[key] for t in team_list]
        return {"min": min(vals), "max": max(vals), "spread": round(max(vals) - min(vals), 2)}

    balanced = all(
        spread(k)["spread"] == 0
        for k in ("capital", "evidence_credits", "founder_hours", "market_potential")
    )
    return {
        "balanced": balanced,
        "capital": spread("capital"),
        "credits": spread("evidence_credits"),
        "hours": spread("founder_hours"),
        "market_potential": spread("market_potential"),
    }


def _alignment(props, key="tokens"):
    """Tokens-weighted average evidence support (0..1) for an allocation."""
    total = sum(max(0, p[key] or 0) for p in props)
    if total <= 0:
        return None  # no tokens allocated => undefined
    weighted = sum((p[key] or 0) * (p["evidence_strength"] or 0) / 10.0 for p in props)
    return weighted / total


def preview_vp_auction(team_id, allocations):
    """Compute (without committing) the auction outcome for a proposed allocation.

    allocations: {vp_id: tokens}. Returns a dict describing tax, dividend, net,
    and per-VP breakdown so the student can see consequences before submitting.
    """
    props = db.list_value_props(team_id)
    if not props:
        return {"ok": False, "reason": "No value propositions defined."}
    if len(props) < content.MIN_VALUE_PROPS:
        return {"ok": False,
                "reason": f"Field at least {content.MIN_VALUE_PROPS} value propositions "
                          f"(you have {len(props)})."}
    total = sum(max(0, int(allocations.get(p["id"], 0))) for p in props)
    if total <= 0:
        return {"ok": False, "reason": "Allocate at least some Venture Tokens."}
    if total > content.VENTURE_TOKEN_POOL:
        return {"ok": False,
                "reason": f"Allocation ({total}) exceeds the {content.VENTURE_TOKEN_POOL}-token pool."}

    proposed = [{**p, "tokens": int(allocations.get(p["id"], 0))} for p in props]
    alignment = _alignment(proposed, "tokens")

    # The "previous" allocation is the team's currently committed one (in `tokens`).
    # It is undefined (None) until the team has run at least one prior auction.
    prev_total = sum(max(0, p["tokens"] or 0) for p in props)
    prev_alignment = _alignment(props, "tokens") if prev_total > 0 else None

    tax = round((1 - alignment) * content.OVERCONFIDENCE_TAX_MAX, 1)
    if prev_alignment is None:
        dividend = 0.0
    else:
        dividend = round(max(0.0, alignment - prev_alignment) * content.LEARNING_DIVIDEND_MAX, 1)
    net = round(dividend - tax, 1)

    breakdown = []
    for p in proposed:
        support = (p["evidence_strength"] or 0) / 10.0
        breakdown.append({
            "id": p["id"], "name": p["name"], "tokens": p["tokens"],
            "evidence_strength": p["evidence_strength"] or 0,
            "unsupported_tokens": round(p["tokens"] * (1 - support), 1),
        })
    return {
        "ok": True, "total_tokens": total, "alignment": round(alignment, 3),
        "prev_alignment": None if prev_alignment is None else round(prev_alignment, 3),
        "tax": tax, "dividend": dividend, "net": net, "breakdown": breakdown,
    }


def run_vp_auction(team_id, allocations, round_no):
    """Commit an auction round: save allocations, apply the net credit change,
    snapshot prev_tokens, and record the result. Returns the preview dict plus
    a committed flag.
    """
    result = preview_vp_auction(team_id, allocations)
    if not result.get("ok"):
        return result

    props = db.list_value_props(team_id)
    # Snapshot current tokens as prev, then store the new allocation.
    for p in props:
        new_tokens = int(allocations.get(p["id"], 0))
        db.update_value_prop(p["id"], prev_tokens=p["tokens"], tokens=new_tokens)

    note = (f"Alignment {result['alignment']} "
            f"(prev {result['prev_alignment']}); "
            f"tax {result['tax']}, dividend {result['dividend']}")
    db.record_vp_result(
        team_id, round_no, result["total_tokens"], result["alignment"],
        result["prev_alignment"], result["tax"], result["dividend"],
        result["net"], note,
    )
    if result["net"] != 0:
        db.adjust_resources(
            team_id, credits=result["net"], kind="vp_auction",
            description=note, allow_negative=True,
        )
    result["committed"] = True
    return result


def experiment_efficiency(team_id):
    """Learning (evidence strength) generated per dollar and founder-hour."""
    exps = db.list_experiments(team_id)
    strength = sum(e["evidence_strength"] for e in exps
                   if e["outcome"] in ("Supported", "Refuted"))
    money = sum(e["cost_money"] for e in exps)
    hours = sum(e["cost_time"] for e in exps)
    return {
        "experiments": len(exps),
        "resolved": sum(1 for e in exps if e["outcome"] in ("Supported", "Refuted")),
        "strength_per_dollar": round(strength / money, 3) if money else 0,
        "strength_per_hour": round(strength / hours, 3) if hours else 0,
    }
