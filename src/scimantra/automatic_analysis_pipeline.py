"""Structured automatic analysis pipeline for SciMantra Research OS."""
from __future__ import annotations
from typing import Any

STEPS = ["Dataset registered", "Data structure checked", "Analysis choice recorded", "Assumptions checked", "Analysis executed", "Result recorded", "Figure/Table linked"]
STATUSES = ["Not started", "Ready", "Needs review", "Complete", "Blocked"]

def new_pipeline(dataset_id: str = "") -> dict[str, Any]:
    return {"dataset_id": dataset_id, "analysis": "", "outcome": "", "steps": {s: "Not started" for s in STEPS}, "notes": ""}

def audit(pipeline: dict[str, Any]) -> dict[str, Any]:
    steps = pipeline.get("steps", {})
    missing = [s for s in STEPS if not steps.get(s)]
    blocked = [s for s in STEPS if steps.get(s) == "Blocked"]
    complete = sum(steps.get(s) == "Complete" for s in STEPS)
    issues = []
    if not pipeline.get("dataset_id"): issues.append("Dataset is not linked.")
    if not pipeline.get("analysis"): issues.append("Analysis choice is not recorded.")
    if not pipeline.get("outcome"): issues.append("Primary outcome is not recorded.")
    if missing: issues.append("One or more pipeline steps have no status.")
    if blocked: issues.append("Blocked steps require resolution before downstream interpretation.")
    return {"complete_steps": complete, "total_steps": len(STEPS), "missing_status": missing, "blocked": blocked, "issues": issues, "ready_for_interpretation": complete == len(STEPS) and not issues}

def next_actions(pipeline: dict[str, Any]) -> list[str]:
    a = audit(pipeline)
    if a["blocked"]: return [f"Resolve blocked step: {x}" for x in a["blocked"]]
    if not pipeline.get("dataset_id"): return ["Link the analysis pipeline to a registered dataset."]
    if not pipeline.get("analysis"): return ["Record the analysis method and rationale."]
    if not pipeline.get("outcome"): return ["Define the primary outcome before interpreting results."]
    return [f"Complete: {x}" for x in STEPS if pipeline.get("steps", {}).get(x) != "Complete"]
