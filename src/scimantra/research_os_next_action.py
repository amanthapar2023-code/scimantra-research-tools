"""Phase 106: evidence-aware next-action prioritization for Research OS.

This layer ranks explicit researcher actions from workflow state, artifact
coverage, and audit signals. It is decision support, not autonomous science.
"""
from __future__ import annotations
from typing import Any

PRIORITIES = ["Critical", "High", "Medium", "Low"]
ACTIONS = [
    "Define research question", "Map literature", "Extract evidence", "Resolve research gap",
    "Form falsifiable hypothesis", "Improve experiment design", "Register dataset",
    "Complete analysis", "Verify result", "Strengthen evidence provenance", "Stress-test claims",
    "Improve manuscript", "Run peer-review challenge", "Complete submission package", "Plan next study",
]

def _priority(score: int) -> str:
    return "Critical" if score >= 90 else "High" if score >= 70 else "Medium" if score >= 40 else "Low"

def recommend(run: dict[str, Any] | None = None, bus: dict[str, Any] | None = None, audit_signals: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    run = run or {}; bus = bus or {}; signals = audit_signals or []
    steps = run.get("steps", [])
    recs = []
    for step in steps:
        status = step.get("status", "Not started")
        deps = step.get("dependencies", [])
        depmap = {s.get("id"): s for s in steps}
        if status == "Complete":
            continue
        score = 50
        reasons = []
        if status == "Blocked": score += 35; reasons.append("workflow step is blocked")
        if all(depmap.get(d, {}).get("status") == "Complete" for d in deps): score += 25; reasons.append("dependencies are complete")
        elif deps: score -= 20; reasons.append("dependencies remain incomplete")
        if not step.get("output_artifact_ids"): score += 10; reasons.append("no output artifact recorded")
        if not step.get("input_artifact_ids") and deps: score += 5; reasons.append("input evidence should be attached")
        recs.append({"action": step.get("name", step.get("id", "Workflow step")), "step_id": step.get("id", ""), "stage": step.get("stage", ""), "tool": step.get("tool", ""), "priority": _priority(max(0, min(100, score))), "score": max(0, min(100, score)), "reason": "; ".join(reasons) or "step is not complete"})
    for s in signals:
        level = str(s.get("level", "")).lower()
        if level in {"critical gap", "critical", "needs work"}:
            score = 95 if "critical" in level else 75
            recs.append({"action": s.get("action") or f"Review {s.get('signal','audit signal')}", "step_id": "audit", "stage": s.get("stage", ""), "tool": s.get("source", "Audit"), "priority": _priority(score), "score": score, "reason": f"audit signal: {s.get('signal','')} — {s.get('level','')}"})
    seen = set(); unique = []
    for r in sorted(recs, key=lambda x: (-x["score"], x["stage"], x["action"])):
        key = (r["step_id"], r["action"])
        if key not in seen: seen.add(key); unique.append(r)
    return unique

def summary(recommendations: list[dict[str, Any]]) -> dict[str, Any]:
    return {"total": len(recommendations), "critical": sum(r.get("priority") == "Critical" for r in recommendations), "high": sum(r.get("priority") == "High" for r in recommendations), "medium": sum(r.get("priority") == "Medium" for r in recommendations), "low": sum(r.get("priority") == "Low" for r in recommendations), "top_action": recommendations[0]["action"] if recommendations else "No action identified"}

def export_markdown(recommendations: list[dict[str, Any]]) -> str:
    lines = ["# SciMantra Research OS — Next-Action Queue", "", "| Priority | Score | Action | Stage | Tool | Reason |", "|---|---:|---|---|---|---|"]
    lines += [f"| {r['priority']} | {r['score']} | {r['action']} | {r['stage']} | {r['tool']} | {r['reason']} |" for r in recommendations]
    return "\n".join(lines)
