"""Phase 105: explicit, human-in-the-loop workflow orchestration for Research OS.

The runner chains registered artifacts and lifecycle steps. It does not execute
scientific methods, invent results, or infer scientific validity.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import json
from typing import Any

from .research_os_data_bus import ensure_bus, link_artifacts, record_event
from .research_os_tool_adapters import TOOL_REGISTRY

STATUSES = ["Not started", "Ready", "In progress", "Blocked", "Complete"]

WORKFLOWS = {
    "Idea → Evidence → Hypothesis": [
        ("question", "Research question", "01 Research Question", "Research Question", "Question", []),
        ("literature", "Literature mapping", "02 Literature", "Literature", "Literature", ["question"]),
        ("evidence", "Evidence extraction", "07 Evidence", "Evidence", "Evidence", ["literature"]),
        ("gap", "Research gap", "02 Literature", "Research Gap", "Research gap", ["evidence"]),
        ("hypothesis", "Falsifiable hypothesis", "03 Hypothesis", "Question & Hypothesis Forge", "Hypothesis", ["gap"]),
    ],
    "Hypothesis → Experiment → Result": [
        ("hypothesis", "Falsifiable hypothesis", "03 Hypothesis", "Question & Hypothesis Forge", "Hypothesis", []),
        ("experiment", "Experiment design", "04 Experiment", "Experiment Architect", "Protocol", ["hypothesis"]),
        ("data", "Experiment → data registration", "05 Data", "Experiment → Data Bridge", "Dataset", ["experiment"]),
        ("analysis", "Analysis pipeline", "06 Analysis", "Automatic Analysis Pipeline", "Analysis", ["data"]),
        ("result", "Result registration", "06 Analysis", "Results Interpreter", "Result", ["analysis"]),
        ("figure", "Figure / table output", "06 Analysis", "Publication Figure Engine", "Figure", ["result"]),
    ],
    "Result → Manuscript → Submission": [
        ("result", "Verified result", "06 Analysis", "Results Interpreter", "Result", []),
        ("evidence", "Evidence / provenance", "07 Evidence", "Evidence Provenance", "Evidence", ["result"]),
        ("claim", "Claim stress test", "08 Claims", "Claim Stress Test", "Claim", ["evidence"]),
        ("manuscript", "Evidence-grounded manuscript", "09 Manuscript", "Evidence-Grounded Manuscript", "Manuscript", ["claim"]),
        ("review", "Hostile peer-review challenge", "10 Peer Review", "Hostile Peer Review", "Review", ["manuscript"]),
        ("submission", "Submission package", "11 Submission", "Submission Package Builder", "Other", ["review"]),
    ],
    "Full Research Cycle": [
        ("question", "Research question", "01 Research Question", "Research Question", "Question", []),
        ("literature", "Literature mapping", "02 Literature", "Literature", "Literature", ["question"]),
        ("gap", "Research gap", "02 Literature", "Research Gap", "Research gap", ["literature"]),
        ("hypothesis", "Hypothesis", "03 Hypothesis", "Question & Hypothesis Forge", "Hypothesis", ["gap"]),
        ("experiment", "Experiment design", "04 Experiment", "Experiment Architect", "Protocol", ["hypothesis"]),
        ("data", "Data registration", "05 Data", "Experiment → Data Bridge", "Dataset", ["experiment"]),
        ("analysis", "Analysis", "06 Analysis", "Automatic Analysis Pipeline", "Analysis", ["data"]),
        ("result", "Result", "06 Analysis", "Results Interpreter", "Result", ["analysis"]),
        ("evidence", "Evidence / provenance", "07 Evidence", "Evidence Provenance", "Evidence", ["result"]),
        ("claim", "Claim audit", "08 Claims", "Claim Stress Test", "Claim", ["evidence"]),
        ("manuscript", "Manuscript", "09 Manuscript", "Evidence-Grounded Manuscript", "Manuscript", ["claim"]),
        ("review", "Peer review challenge", "10 Peer Review", "Hostile Peer Review", "Review", ["manuscript"]),
        ("submission", "Submission", "11 Submission", "Submission Package Builder", "Other", ["review"]),
        ("next_study", "Next study / reuse", "12 Next Study", "Impact / Reuse Engine", "Research question", ["submission"]),
    ],
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _steps(workflow_id: str) -> list[dict[str, Any]]:
    if workflow_id not in WORKFLOWS:
        raise ValueError(f"Unknown workflow: {workflow_id}")
    rows = []
    for idx, (sid, name, stage, tool, output_type, deps) in enumerate(WORKFLOWS[workflow_id], 1):
        rows.append({"id": sid, "order": idx, "name": name, "stage": stage, "tool": tool, "output_type": output_type, "dependencies": list(deps), "status": "Not started", "input_artifact_ids": [], "output_artifact_ids": [], "note": ""})
    return rows


def new_run(workflow_id: str, project: dict[str, Any] | None = None) -> dict[str, Any]:
    if workflow_id not in WORKFLOWS:
        raise ValueError(f"Unknown workflow: {workflow_id}")
    return {"schema_version": 1, "run_id": f"RUN-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}", "workflow_id": workflow_id, "project": deepcopy(project or {}), "steps": _steps(workflow_id), "created_at": _now(), "updated_at": _now()}


def _artifact_ids(bus: dict[str, Any]) -> set[str]:
    return {a.get("id") for a in ensure_bus(bus).get("artifacts", []) if a.get("id")}


def available_steps(run: dict[str, Any], bus: dict[str, Any]) -> list[str]:
    ids = _artifact_ids(bus)
    by_id = {s["id"]: s for s in run.get("steps", [])}
    available = []
    for step in run.get("steps", []):
        if step.get("status") in {"Complete", "In progress"}:
            continue
        deps_ok = all(by_id.get(d, {}).get("status") == "Complete" for d in step.get("dependencies", []))
        if deps_ok and all(x in ids for x in step.get("input_artifact_ids", [])):
            available.append(step["id"])
        elif not step.get("dependencies") and not step.get("input_artifact_ids"):
            available.append(step["id"])
    return available


def advance(run: dict[str, Any], step_id: str, status: str, input_artifact_ids: list[str] | None = None, output_artifact_ids: list[str] | None = None, note: str = "") -> dict[str, Any]:
    if status not in STATUSES:
        raise ValueError(f"Unsupported status: {status}")
    out = deepcopy(run)
    step = next((s for s in out.get("steps", []) if s.get("id") == step_id), None)
    if step is None:
        raise ValueError(f"Unknown workflow step: {step_id}")
    step["status"] = status
    if input_artifact_ids is not None: step["input_artifact_ids"] = [x.strip() for x in input_artifact_ids if x.strip()]
    if output_artifact_ids is not None: step["output_artifact_ids"] = [x.strip() for x in output_artifact_ids if x.strip()]
    if note: step["note"] = note.strip()
    out["updated_at"] = _now()
    return out


def link_step_artifacts(run: dict[str, Any], bus: dict[str, Any], step_id: str) -> dict[str, Any]:
    step = next((s for s in run.get("steps", []) if s.get("id") == step_id), None)
    if step is None: raise ValueError(f"Unknown workflow step: {step_id}")
    out = ensure_bus(bus)
    for source in step.get("input_artifact_ids", []):
        for target in step.get("output_artifact_ids", []):
            out = link_artifacts(out, source, target, "derived_from", f"Workflow {run['workflow_id']} / {step_id}")
    return record_event(out, "Researcher", "Workflow step linked", step_id, "workflow_step", run["workflow_id"])


def audit_run(run: dict[str, Any], bus: dict[str, Any]) -> dict[str, Any]:
    ids = _artifact_ids(bus)
    by_id = {s["id"]: s for s in run.get("steps", [])}
    issues = []
    ready = []
    blocked = []
    for step in run.get("steps", []):
        missing_inputs = [x for x in step.get("input_artifact_ids", []) if x not in ids]
        missing_deps = [d for d in step.get("dependencies", []) if by_id.get(d, {}).get("status") != "Complete"]
        if missing_inputs: issues.append({"step": step["id"], "issue": "Missing input artifacts", "details": ", ".join(missing_inputs)})
        if missing_deps: issues.append({"step": step["id"], "issue": "Dependencies incomplete", "details": ", ".join(missing_deps)})
        if step["status"] == "Blocked": blocked.append(step["id"])
        if step["id"] in available_steps(run, bus): ready.append(step["id"])
    complete = sum(s.get("status") == "Complete" for s in run.get("steps", []))
    total = len(run.get("steps", []))
    return {"run_id": run.get("run_id"), "workflow": run.get("workflow_id"), "steps": total, "complete": complete, "ready": ready, "blocked": blocked, "issues": issues, "completion_pct": round(100 * complete / total, 1) if total else 0.0, "ready_to_finish": total > 0 and complete == total and not issues}


def summary(run: dict[str, Any], bus: dict[str, Any]) -> dict[str, Any]:
    a = audit_run(run, bus)
    return {"workflow": a["workflow"], "steps": a["steps"], "complete": a["complete"], "ready": len(a["ready"]), "blocked": len(a["blocked"]), "issues": len(a["issues"]), "completion_pct": a["completion_pct"]}


def export_run(run: dict[str, Any], bus: dict[str, Any]) -> str:
    return json.dumps({"run": run, "audit": audit_run(run, bus), "bus_summary": {"artifacts": len(ensure_bus(bus).get("artifacts", [])), "links": len(ensure_bus(bus).get("links", []))}}, indent=2, ensure_ascii=False)


def workflow_contracts() -> list[dict[str, str]]:
    return [{"workflow": name, "steps": str(len(steps))} for name, steps in WORKFLOWS.items()]
