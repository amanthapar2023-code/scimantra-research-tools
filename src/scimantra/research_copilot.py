"""Project-level cockpit that connects SciMantra research modules."""
from __future__ import annotations
from typing import Any

def project_health(*, evidence: float = 0, design: float = 0, reviewer: float = 0, traceability: float = 0, reproducibility: float = 0, graph: float = 0) -> dict[str, Any]:
    values = {"Evidence": evidence, "Design": design, "Reviewer readiness": reviewer, "Claim traceability": traceability, "Reproducibility": reproducibility, "Research graph": graph}
    clean = {k: max(0.0, min(100.0, float(v))) for k, v in values.items()}
    score = sum(clean.values()) / len(clean) if clean else 0.0
    return {"score": round(score, 1), "components": clean, "label": "Strong" if score >= 80 else "Developing" if score >= 60 else "Needs attention"}

def cockpit_actions(health: dict[str, Any]) -> list[str]:
    return [f"Strengthen {name}" for name, value in health.get("components", {}).items() if value < 70]

def project_snapshot(title: str, health: dict[str, Any], memory_count: int = 0) -> dict[str, Any]:
    return {"Research title": title or "Untitled project", "Project health": health.get("score", 0), "Health label": health.get("label", ""), "Memory entries": memory_count, "Priority actions": cockpit_actions(health)}
