"""Session usage limits for SciMantra Free and Pro plans.

This is a safe application-layer limiter. For production enforcement across
multiple devices, persist counters server-side and enforce them in a trusted
backend as well.
"""
from __future__ import annotations

from datetime import date

from src.scimantra.subscription import get_subscription

FREE_LIMITS = {
    "dataset_uploads": 5,
    "analysis_runs": 10,
    "report_exports": 3,
    "figure_exports": 3,
    "ai_requests": 5,
}

PRO_LIMITS = {key: None for key in FREE_LIMITS}


def _state(state: dict) -> dict:
    today = date.today().isoformat()
    usage = state.setdefault("scimantra_usage", {"date": today, "counts": {}})
    if usage.get("date") != today:
        usage.clear()
        usage.update({"date": today, "counts": {}})
    return usage


def limit_for(state: dict, action: str):
    sub = get_subscription(state)
    return PRO_LIMITS[action] if sub.is_pro else FREE_LIMITS[action]


def used(state: dict, action: str) -> int:
    return int(_state(state)["counts"].get(action, 0))


def can_use(state: dict, action: str) -> bool:
    limit = limit_for(state, action)
    return limit is None or used(state, action) < limit


def record(state: dict, action: str) -> bool:
    if not can_use(state, action):
        return False
    usage = _state(state)
    usage["counts"][action] = used(state, action) + 1
    return True


def usage_snapshot(state: dict) -> dict:
    return {action: {"used": used(state, action), "limit": limit_for(state, action)} for action in FREE_LIMITS}
