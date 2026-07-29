"""
logic.py — Shared game logic: valuation, evidence economy, dashboard aggregation,
and the editable schedule (round -> topic -> advance time).

Kept free of Streamlit so it can be unit-tested and reused.
"""

import json
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


# --------------------------------------------------------------------------- #
# Balanced auto-arrangement
#   Each topic has a "load" (how much material it is). We split the ordered
#   curriculum into as many contiguous groups as there are rounds, minimizing the
#   heaviest round — so related concepts stay together and no round is overloaded.
# --------------------------------------------------------------------------- #
def topic_load(topic):
    """A rough effort weight for a topic: its concepts plus objectives."""
    if not topic:
        return 0
    return len(topic.get("concepts", [])) + len(topic.get("objectives", []))


def _balanced_group_sizes(weights, k):
    """Split a sequence of weights into k contiguous groups minimizing the max
    group sum (classic linear-partition DP). Returns a list of k group sizes.
    """
    n = len(weights)
    if k <= 1:
        return [n]
    if k >= n:
        return [1] * n + [0] * (k - n)
    prefix = [0]
    for w in weights:
        prefix.append(prefix[-1] + w)
    INF = float("inf")
    dp = [[INF] * (k + 1) for _ in range(n + 1)]
    back = [[0] * (k + 1) for _ in range(n + 1)]
    dp[0][0] = 0
    for i in range(1, n + 1):
        for j in range(1, min(i, k) + 1):
            for p in range(j - 1, i):
                seg = prefix[i] - prefix[p]
                cost = max(dp[p][j - 1], seg)
                if cost < dp[i][j]:
                    dp[i][j] = cost
                    back[i][j] = p
    sizes, i, j = [], n, k
    while j > 0:
        p = back[i][j]
        sizes.append(i - p)
        i, j = p, j - 1
    sizes.reverse()
    return sizes


def suggest_balanced_layout(n_rounds=None, order=None):
    """Suggest a balanced arrangement: {round: [topic_key, ...]}.

    Topics are taken in their logical curriculum order and split into contiguous
    groups so that related concepts stay together and the heaviest round is as
    light as possible.
    """
    n_rounds = int(n_rounds or total_rounds())
    order = order or content.DEFAULT_TOPIC_ORDER
    weights = [topic_load(content.CURRICULUM_BY_KEY[k]) for k in order]
    sizes = _balanced_group_sizes(weights, n_rounds)
    layout, idx = {}, 0
    for r, size in enumerate(sizes, start=1):
        layout[r] = order[idx:idx + size]
        idx += size
    return layout


def layout_load_summary(layout):
    """For a {round:[keys]} layout, return [{round, titles, load, count}]."""
    out = []
    for r in sorted(layout):
        keys = layout[r]
        out.append({
            "round": r,
            "titles": " + ".join(content.CURRICULUM_BY_KEY[k]["title"] for k in keys) or "—",
            "load": sum(topic_load(content.CURRICULUM_BY_KEY[k]) for k in keys),
            "count": len(keys),
        })
    return out


def apply_layout(layout):
    """Replace the whole schedule assignment with the given {round:[keys]} layout."""
    for tp in content.CURRICULUM_TOPICS:
        db.remove_round_topic(tp["key"])
    for r in sorted(layout):
        for pos, key in enumerate(layout[r]):
            db.set_topic_placement(key, r, pos)


def round_load(rnd):
    """Total load currently assigned to a round."""
    return sum(topic_load(t) for t in topics_for_round(rnd))


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


# --------------------------------------------------------------------------- #
# Auto-Director (autopilot)
#
# Derives the Director's per-round decisions from each team's actual round input
# (their canvases, evidence, experiments, assumptions, auction, AI logs, etc.):
#   • predicted dashboard scores (0–100) per dimension
#   • a suggested market event aimed at the team's biggest exposed risk
#   • a recommended decision for each pending pivot petition
# Every suggestion is just that — the Director can override before applying.
# --------------------------------------------------------------------------- #
def _clamp100(x):
    return int(max(0, min(100, round(x))))


def _filled_blocks(canvas):
    if not canvas:
        return 0, 0
    data = canvas.get("data", {}) or {}
    total = len(data)
    filled = sum(1 for v in data.values() if v and str(v).strip())
    return filled, total


def default_score_weights():
    """Per-dimension weight multipliers, default 1.0 for every dimension."""
    return {dim: 1.0 for dim in content.DIMENSION_NAMES}


def get_score_weights():
    """Load the Director's tunable per-dimension weights (1.0 = default)."""
    raw = db.get_setting("score_weights")
    weights = default_score_weights()
    if raw:
        try:
            saved = json.loads(raw)
            for dim in weights:
                if dim in saved:
                    weights[dim] = float(saved[dim])
        except (ValueError, TypeError):
            pass
    return weights


def set_score_weights(weights):
    clean = {dim: round(float(weights.get(dim, 1.0)), 2) for dim in content.DIMENSION_NAMES}
    db.set_setting("score_weights", json.dumps(clean))


def _raw_scores(team_id):
    """Compute the UNWEIGHTED heuristic score for each dimension (0..~100 floats)."""
    ev = evidence_summary(team_id)
    risk = assumption_risk_report(team_id)
    eff = experiment_efficiency(team_id)

    cp = db.latest_canvas(team_id, "customer_profile")
    vpc = db.latest_canvas(team_id, "vpc")
    bmc = db.latest_canvas(team_id, "bmc")
    cp_filled, _ = _filled_blocks(cp)
    vpc_filled, _ = _filled_blocks(vpc)
    bmc_filled, _ = _filled_blocks(bmc)

    cp_versions = len(db.list_canvases(team_id, "customer_profile"))
    all_versions = len(db.list_canvases(team_id))
    vp_results = db.list_vp_results(team_id)
    latest_align = vp_results[0]["alignment"] if vp_results else 0.0

    approved_pivots = sum(1 for p in db.list_pivots(team_id)
                          if p["status"] in ("Approved", "Conditional"))
    reflections = len(db.list_reflections(team_id))
    ai_logs = db.list_ai_logs(team_id)
    ai_verified = sum(1 for l in ai_logs if l["status"] in ("Verified", "Modified"))
    ai_rate = (ai_verified / len(ai_logs)) if ai_logs else None

    bmc_data = (bmc or {}).get("data", {}) if bmc else {}
    has_revenue = bool(str(bmc_data.get("revenue_streams", "")).strip())
    has_cost = bool(str(bmc_data.get("cost_structure", "")).strip())
    pricing_exps = sum(1 for e in db.list_experiments(team_id)
                       if "price" in (e["card_type"] or "").lower()
                       or "preorder" in (e["card_type"] or "").lower())

    raw = {}
    raw["Customer Insight"] = (50 * (cp_filled / 3) + min(20, max(0, cp_versions - 1) * 10)
                               + min(30, ev["behavioral"] * 5))
    raw["Value Proposition Fit"] = 50 * (vpc_filled / 6) + 50 * float(latest_align or 0)
    raw["Evidence Strength"] = ev["avg_strength"] * 8 + min(20, ev["behavioral"] * 4)
    raw["Business-Model Coherence"] = 100 * (bmc_filled / 9)
    raw["Experiment Efficiency"] = eff["resolved"] * 20 + (eff["experiments"] - eff["resolved"]) * 5
    raw["Financial Viability"] = ((25 if has_revenue else 0) + (25 if has_cost else 0)
                                  + min(30, risk["supported"] * 10) + (20 if pricing_exps else 0))
    raw["Adaptability"] = all_versions * 8 + approved_pivots * 20
    raw["Responsible Innovation"] = 50 + (50 * ai_rate if ai_rate is not None else 0)
    raw["Team Execution"] = reflections * 15 + min(40, (eff["experiments"] + ev["count"]) * 4)
    raw["Investor Confidence"] = (0.4 * raw["Evidence Strength"]
                                  + 0.3 * raw["Business-Model Coherence"]
                                  + 0.3 * raw["Value Proposition Fit"]
                                  - len(risk["exposed"]) * 5)
    return raw


# Each dashboard dimension only becomes fair to score once the tool it depends on
# has been introduced. This keeps Auto-Director recommendations aligned with the
# options actually available in a given round.
_DIMENSION_TOOL = {
    "Customer Insight": "Canvases",
    "Value Proposition Fit": "VP Auction",
    "Evidence Strength": "Evidence Ledger",
    "Experiment Efficiency": "Experiment Marketplace",
    "Financial Viability": "Experiment Marketplace",
    "Adaptability": "Pivot Petition",
    "Responsible Innovation": None,   # AI Assist is a base tool (always available)
    "Team Execution": None,           # Decision Journal is a base tool
}


def dimension_available(dim, round_no):
    """Is a dashboard dimension 'in play' (its tool introduced) by this round?"""
    if dim == "Business-Model Coherence":
        return round_no >= canvas_unlock_round("bmc")
    if dim == "Investor Confidence":
        return round_no >= canvas_unlock_round("bmc")   # needs a business model to judge
    page = _DIMENSION_TOOL.get(dim)
    return page is None or round_no >= page_unlock_round(page)


def available_dimensions(round_no):
    """Dimensions whose underlying tool has been introduced by this round."""
    return [d for d in content.DIMENSION_NAMES if dimension_available(d, round_no)]


def auto_scores(team_id, weights=None, round_no=None, only_available=True):
    """Predict 0–100 dashboard scores from a team's submitted work.

    Each dimension's raw heuristic score is multiplied by the Director's tunable
    weight (default 1.0) and clamped to 0–100. When `round_no` is given and
    `only_available` is True, only dimensions whose tools are introduced by that
    round are returned — so recommendations match what teams could actually do.
    """
    raw = _raw_scores(team_id)
    weights = weights or get_score_weights()
    scores = {dim: _clamp100(raw[dim] * weights.get(dim, 1.0))
              for dim in content.DIMENSION_NAMES}
    if round_no is not None and only_available:
        avail = set(available_dimensions(round_no))
        scores = {d: v for d, v in scores.items() if d in avail}
    return scores


def valuation_from_scores(team_id, scores):
    """Predicted valuation from a set of (possibly not-yet-saved) scores."""
    team = db.get_team(team_id)
    if not team:
        return None
    value = (team["market_potential"]
             * _index_from_score(scores.get("Evidence Strength"))
             * _index_from_score(scores.get("Business-Model Coherence"))
             * _index_from_score(scores.get("Team Execution"))
             - (team["unresolved_risk"] or 0))
    return round(value, 0)


def apply_scores(team_id, round_no, scores):
    for dim, val in scores.items():
        db.set_score(team_id, round_no, dim, val)


# Map the risk type of a team's biggest exposed assumption to an event category.
_RISK_TO_EVENT = {
    "Desirability": "Customer",
    "Feasibility": "Operational",
    "Viability": "Financial",
    "Adaptability": "Competitive",
}


def suggest_event(team_id, round_no=None):
    """Suggest a market event aimed at the team's biggest exposed risk.

    Returns {category, text, exposes, reason}. Falls back to the round's topic
    when the team has no exposed assumption yet.
    """
    import random
    risk = assumption_risk_report(team_id)
    category = None
    reason = ""
    if risk["exposed"]:
        top = risk["exposed"][0]
        category = _RISK_TO_EVENT.get(top["risk_type"])
        reason = f"Targets untested {top['risk_type']} assumption: “{top['text']}”."
    if not category:
        # Fall back to the current round's canvas focus / topic flavor.
        rnd = round_no or db.current_round()
        focuses = canvas_focus_for_round(rnd)
        if "bmc" in focuses:
            category = "Competitive"
        elif focuses:
            category = "Customer"
        else:
            category = random.choice(list(content.MARKET_EVENTS.keys()))
        reason = "No high-risk untested assumption yet — chosen from this round's focus."
    text, exposes = random.choice(content.MARKET_EVENTS[category])
    return {"category": category, "text": text, "exposes": exposes, "reason": reason}


def recommend_pivot(pivot):
    """Recommend a committee decision for a pivot petition from its completeness."""
    has_evidence = bool((pivot.get("challenge_evid") or "").strip())
    has_change = bool((pivot.get("proposed_change") or "").strip())
    has_new = bool((pivot.get("new_assumptions") or "").strip())
    has_needed = bool((pivot.get("evidence_needed") or "").strip())
    if not has_change or not (pivot.get("original_assum") or "").strip():
        return "Rejected", "Missing the original assumption or a concrete proposed change."
    if not has_evidence:
        return "NeedsEvidence", "No challenging evidence cited — ask the team to test first."
    if has_evidence and has_new and has_needed:
        cost = pivot.get("change_cost") or 0
        if cost and cost > 1000:
            return "Conditional", "Evidence-based, but costly — approve subject to milestones."
        return "Approved", "Evidence cited and new assumptions/tests defined — disciplined pivot."
    return "Conditional", "Partly justified — approve conditionally and request the missing pieces."


# ---- Per-round feedback "email" ------------------------------------------- #
def generate_feedback(team_id, round_no=None, scores=None):
    """Compose a per-round feedback email for a team from its predicted performance.

    Returns {subject, body}. Highlights strengths and weak spots, evidence quality,
    exposed risks, the market event they face, and a concrete next step.
    """
    team = db.get_team(team_id)
    rnd = round_no or db.current_round()
    scores = scores or auto_scores(team_id, round_no=rnd)  # only dimensions in play
    ev = evidence_summary(team_id)
    risk = assumption_risk_report(team_id)

    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    strengths = [d for d, s in ranked[:3] if s >= 55]
    weak = [d for d, s in ranked[::-1][:3] if s <= 55]
    pred_val = valuation_from_scores(team_id, scores)

    lines = [f"Hi {team['name']},", "",
             f"Here's your Round {rnd} venture review from the Foundry.", ""]
    lines.append(f"Predicted venture valuation: ${pred_val:,.0f}")
    lines.append("")
    if strengths:
        lines.append("What's working:")
        for d in strengths:
            lines.append(f"  • {d} ({scores[d]}/100)")
        lines.append("")
    if weak:
        lines.append("Where to focus next:")
        for d in weak:
            lines.append(f"  • {d} ({scores[d]}/100)")
        lines.append("")

    lines.append(f"Evidence: {ev['count']} logged, {ev['behavioral']} behavioral "
                 f"(avg strength {ev['avg_strength']}/10). "
                 + ("Strong behavioral base — keep it up."
                    if ev['behavioral'] >= 3 else
                    "Push for more behavioral evidence (trials, LOIs, preorders) over opinions."))
    lines.append("")

    if risk["exposed"]:
        lines.append("⚠️ High-risk assumptions you haven't tested yet:")
        for a in risk["exposed"][:3]:
            lines.append(f"  • {a['text']} ({a['risk_type']})")
        top = risk["exposed"][0]
        lines.append("")
        lines.append(f"Recommended next step: design the cheapest experiment that could "
                     f"disprove “{top['text']}”, set a success/failure threshold in advance, "
                     f"and run it before you invest further.")
    else:
        lines.append("Recommended next step: convert your latest learning into your next "
                     "canvas version and line up the next assumption to test.")

    # Reference the newest market event they were dealt, if any.
    events = [e for e in db.list_events(team_id) if e["round"] == rnd]
    if events:
        e = events[0]
        lines.append("")
        lines.append(f"Market watch ({e['category']}): {e['text']} "
                     f"This pressures the assumption: {e['exposes']}")

    lines.append("")
    lines.append("— The Venture Foundry Director")
    return {"subject": f"Round {rnd} venture review — {team['name']}",
            "body": "\n".join(lines)}


def send_feedback(team_id, round_no=None, scores=None):
    fb = generate_feedback(team_id, round_no, scores)
    db.add_message(team_id, fb["subject"], fb["body"], round_no or db.current_round())
    return fb


# ---- Automation settings & batch run -------------------------------------- #
def auto_flag(key, default=True):
    val = db.get_setting(key)
    if val is None:
        return default
    return str(val) == "1"


def set_auto_flag(key, value):
    db.set_setting(key, "1" if value else "0")


def run_autopilot(round_no=None, teams=None):
    """Apply enabled automation for a round. Returns a per-team summary.

    Idempotent-ish: scores overwrite for the round; an event is only issued to a
    team that has none for that round; pending pivots are decided by recommendation.
    """
    rnd = round_no or db.current_round()
    teams = teams if teams is not None else db.list_teams()
    events_open = rnd >= page_unlock_round("Market Events")
    pivots_open = rnd >= page_unlock_round("Pivot Petition")
    summary = []
    for t in teams:
        entry = {"team": t["name"], "team_id": t["id"], "scored": False,
                 "event": None, "pivots": 0}
        if auto_flag("auto_scoring_on"):
            sc = auto_scores(t["id"], round_no=rnd)   # only dimensions in play this round
            apply_scores(t["id"], rnd, sc)
            entry["scored"] = True
        if auto_flag("auto_events_on") and events_open:
            existing = [e for e in db.list_events(t["id"], include_broadcast=False)
                        if e["round"] == rnd]
            if not existing:
                ev = suggest_event(t["id"], rnd)
                db.add_event(t["id"], rnd, ev["category"], ev["text"], ev["exposes"])
                entry["event"] = ev["category"]
        if auto_flag("auto_pivots_on") and pivots_open:
            for p in db.list_pivots(t["id"]):
                if p["status"] == "Submitted":
                    dec, note = recommend_pivot(p)
                    db.decide_pivot(p["id"], dec, "[auto] " + note)
                    if dec in ("Approved", "Conditional") and (p["change_cost"] or 0):
                        db.adjust_resources(t["id"], money=-p["change_cost"], kind="pivot",
                                            description="Pivot change cost (auto)",
                                            allow_negative=True)
                    entry["pivots"] += 1
        if auto_flag("auto_feedback_on"):
            send_feedback(t["id"], rnd)
            entry["feedback"] = True
        summary.append(entry)
    return summary
