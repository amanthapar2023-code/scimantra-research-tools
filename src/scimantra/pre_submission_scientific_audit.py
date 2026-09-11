"""Unified pre-submission scientific readiness audit."""
from __future__ import annotations
from typing import Any

SIGNALS = ["Evidence sufficiency", "Claim stress test", "Causal validity", "Bias / error", "Statistical readiness", "Robustness", "Reproducibility", "Generalizability", "Mechanism consistency", "Novelty / prior art", "Reviewer risk"]
LEVELS = ["Not assessed", "Strong", "Adequate", "Needs work", "Critical gap"]
WEIGHTS = {"Strong": 3, "Adequate": 2, "Needs work": 1, "Critical gap": 0, "Not assessed": 0}

def audit(signals: dict[str, str]) -> dict[str, Any]:
    assessed = [v for v in signals.values() if v != "Not assessed"]
    critical = [k for k,v in signals.items() if v == "Critical gap"]
    needs = [k for k,v in signals.items() if v == "Needs work"]
    score = round(100 * sum(WEIGHTS.get(v,0) for v in assessed) / (3 * len(signals)), 1) if signals else 0
    return {"score": score, "assessed": len(assessed), "critical": critical, "needs_work": needs, "ready": bool(assessed) and not critical and not needs}

def actions(result: dict[str, Any]) -> list[str]:
    return [f"Resolve critical gap: {x}" for x in result["critical"]] + [f"Strengthen: {x}" for x in result["needs_work"]] + (["Complete the remaining unassessed scientific checks."] if result["assessed"] == 0 else [])
