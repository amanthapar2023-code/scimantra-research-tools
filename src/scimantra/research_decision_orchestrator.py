"""Integrate research-audit signals into a next-action decision map."""
from __future__ import annotations
from typing import Any

SIGNALS = [
    ("Novelty", "Distinctiveness / prior-art confidence", "Verify prior art or sharpen the contribution"),
    ("Evidence sufficiency", "Direct support for major claims", "Collect, link, or strengthen evidence"),
    ("Causal validity", "Design supports intended causal wording", "Add controls/design evidence or weaken causal language"),
    ("Bias / error", "Residual bias and error risks", "Reduce the highest-impact bias/error source"),
    ("Statistical readiness", "Assumptions and analysis choice", "Re-check assumptions or revise analysis plan"),
    ("Robustness", "Stability under plausible challenges", "Run sensitivity/robustness analyses"),
    ("Reproducibility", "Traceability of analytical workflow", "Document inputs, rules, versions, and outputs"),
    ("Generalizability", "Support for target context", "Define boundaries or gather cross-context evidence"),
    ("Mechanism", "Consistency of explanatory claim", "Test mechanism or qualify explanation"),
    ("Reviewer risk", "Unresolved peer-review vulnerabilities", "Resolve highest-risk reviewer challenge"),
]
LEVELS = ["Not assessed", "Strong", "Adequate", "Needs work", "Critical gap"]
ACTIONS = [
    "Collect more evidence", "Add / improve control", "Change or re-check analysis", "Run validation experiment",
    "Test alternative explanation", "Verify prior art", "Weaken / narrow claim", "Improve reproducibility", "Proceed to manuscript", "Proceed to submission"
]

def template():
    return [{"Signal": n, "What it tests": q, "Status": "Not assessed", "Evidence / module result": "", "Next action": a} for n, q, a in SIGNALS]

def orchestrate(rows: list[dict[str, Any]], readiness: str = "Not assessed") -> dict[str, Any]:
    rank = {"Strong": 0, "Adequate": 20, "Needs work": 60, "Critical gap": 100, "Not assessed": 50}
    risk = round(sum(rank.get(r.get("Status"), 50) for r in rows) / len(rows), 1) if rows else 0
    critical = [r["Signal"] for r in rows if r.get("Status") == "Critical gap"]
    needs = [r["Signal"] for r in rows if r.get("Status") == "Needs work"]
    if critical:
        action = "Resolve critical gaps before submission"
    elif needs:
        action = "Address priority gaps before final manuscript"
    elif all(r.get("Status") == "Strong" for r in rows):
        action = "Proceed to manuscript/submission checks"
    else:
        action = "Complete unassessed checks"
    return {"risk": risk, "critical": len(critical), "needs_work": len(needs), "unassessed": sum(r.get("Status") == "Not assessed" for r in rows), "recommended_action": action, "critical_signals": critical, "needs_signals": needs, "readiness": readiness}

def action_queue(rows):
    rank = {"Critical gap": 100, "Needs work": 70, "Not assessed": 50, "Adequate": 20, "Strong": 0}
    return sorted([{"Priority": rank.get(r.get("Status"), 50), "Signal": r.get("Signal", ""), "Status": r.get("Status", "Not assessed"), "Recommended action": r.get("Next action", "Complete assessment")} for r in rows], key=lambda x: x["Priority"], reverse=True)

def export_orchestration(rows, summary):
    lines = ["# SciMantra Research Decision Orchestrator", "", f"Integrated risk index: {summary['risk']}/100", f"Recommended next step: {summary['recommended_action']}", "", "> This is a decision-support map based on researcher-supplied/module-derived status fields. It does not certify scientific validity or predict publication acceptance.", ""]
    for r in rows:
        lines += [f"## {r['Signal']} — {r['Status']}", f"- Test: {r['What it tests']}", f"- Evidence / module result: {r.get('Evidence / module result','')}", f"- Next action: {r.get('Next action','')}", ""]
    return "\n".join(lines)
