"""Unified project map for connecting the SciMantra research workflow."""
from __future__ import annotations
from typing import Any

STAGES = [
    ("01", "Research question", "Question / gap / objective"),
    ("02", "Literature", "Evidence matrix / prior work"),
    ("03", "Hypothesis", "Testable prediction"),
    ("04", "Experiment", "Design / controls / power"),
    ("05", "Data", "Raw and processed datasets"),
    ("06", "Analysis", "Statistics / models / assumptions"),
    ("07", "Evidence", "Results / figures / provenance"),
    ("08", "Claims", "Interpretation / claim scope"),
    ("09", "Manuscript", "Sections / references / figures"),
    ("10", "Peer review", "Reviewer attacks / responses"),
    ("11", "Readiness", "Integrity / reproducibility / submission"),
]
STATUSES = ["Not started", "In progress", "Needs attention", "Complete"]

def template():
    return [{"ID": i, "Stage": s, "Purpose": p, "Status": "Not started", "Evidence / artifact": "", "Owner / note": ""} for i, s, p in STAGES]

def audit(rows: list[dict[str, Any]]):
    counts = {s: sum(r.get("Status") == s for r in rows) for s in STATUSES}
    missing = [r["Stage"] for r in rows if r.get("Status") != "Complete" and not r.get("Evidence / artifact", "").strip()]
    attention = [r["Stage"] for r in rows if r.get("Status") == "Needs attention"]
    completion = round(100 * counts["Complete"] / len(rows), 1) if rows else 0
    return {"total": len(rows), "completion": completion, "counts": counts, "missing_artifacts": missing, "attention": attention}

def next_steps(rows):
    rank = {"Needs attention": 100, "In progress": 70, "Not started": 50, "Complete": 0}
    return sorted([{"Priority": rank.get(r.get("Status"), 50), "Stage": r.get("Stage", ""), "Status": r.get("Status", "Not started"), "Action": "Resolve stage and attach evidence/artifact" if r.get("Status") == "Needs attention" else "Advance stage and record evidence" if r.get("Status") != "Complete" else "Maintain trace"} for r in rows], key=lambda x: x["Priority"], reverse=True)

def export_workspace(rows, summary):
    lines = ["# SciMantra Unified Research Project Workspace", "", f"Workflow completion: {summary['completion']}%", "", "> This workspace organizes researcher-defined project state. Completion is not a certification of scientific validity, reproducibility, or publication readiness.", ""]
    for r in rows:
        lines += [f"## {r['ID']}. {r['Stage']} — {r['Status']}", f"Purpose: {r['Purpose']}", f"Evidence / artifact: {r.get('Evidence / artifact','')}", f"Owner / note: {r.get('Owner / note','')}", ""]
    return "\n".join(lines)
