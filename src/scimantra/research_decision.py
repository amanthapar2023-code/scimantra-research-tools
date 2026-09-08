"""Evidence-aware ranking of possible next research actions."""
from __future__ import annotations
from typing import Any

ACTIONS = [
    ("Resolve evidence gap", "Missing source-anchored literature or claim evidence", "evidence"),
    ("Strengthen experimental design", "Open control, replication, confounding, or measurement issue", "design"),
    ("Run robustness analysis", "Conclusion may depend on analytical choices", "analysis"),
    ("Test alternative explanation", "A competing mechanism could explain the observed pattern", "experiment"),
    ("Improve reproducibility record", "Protocol, provenance, software, or exception information is incomplete", "reproducibility"),
    ("Validate novelty", "Contribution needs comparison with closest prior work", "novelty"),
]

def rank_actions(evidence_gap: float = 0, design_risk: float = 0, analysis_risk: float = 0, alternative_risk: float = 0, reproducibility_gap: float = 0, novelty_risk: float = 0) -> list[dict[str, Any]]:
    scores = [evidence_gap, design_risk, analysis_risk, alternative_risk, reproducibility_gap, novelty_risk]
    rows = []
    for (action, rationale, _), score in zip(ACTIONS, scores):
        value = max(0.0, min(100.0, float(score)))
        rows.append({"Priority": value, "Recommended next action": action, "Why it matters": rationale})
    return sorted(rows, key=lambda x: x["Priority"], reverse=True)

def decision_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {"top_action": "No action ranked", "priority": 0.0}
    return {"top_action": rows[0]["Recommended next action"], "priority": rows[0]["Priority"]}

def export_decisions(rows: list[dict[str, Any]]) -> str:
    lines = ["# Research Decision Queue", "", "Ranked actions are decision-support prompts, not scientific conclusions.", ""]
    for i, r in enumerate(rows, 1):
        lines.append(f"{i}. **{r['Recommended next action']}** — priority {r['Priority']:.1f}/100 — {r['Why it matters']}")
    return "\n".join(lines)
