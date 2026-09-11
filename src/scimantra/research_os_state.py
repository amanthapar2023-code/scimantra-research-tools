"""Shared project-state primitives for the SciMantra Research OS.

The engine is intentionally storage-agnostic: Streamlit session state, a future
Supabase backend, or another persistence layer can use the same schema.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import json
from typing import Any

STAGE_NAMES = [
    "Research Question", "Literature", "Hypothesis", "Experiment", "Data",
    "Analysis", "Evidence", "Claims", "Manuscript", "Peer Review",
    "Submission", "Next Study",
]
STATUS_VALUES = ["Not started", "In progress", "Blocked", "Ready", "Complete"]


def new_project(name: str = "My Research Project", question: str = "") -> dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    return {
        "schema_version": 1,
        "project": {"name": name.strip() or "My Research Project", "question": question.strip()},
        "created_at": now,
        "updated_at": now,
        "stages": {stage: {"status": "Not started", "notes": "", "outputs": []} for stage in STAGE_NAMES},
        "artifacts": [],
        "links": [],
    }


def normalize_project(project: dict[str, Any] | None) -> dict[str, Any]:
    base = new_project()
    if not isinstance(project, dict):
        return base
    out = deepcopy(base)
    out.update({k: deepcopy(v) for k, v in project.items() if k in {"schema_version", "created_at", "updated_at"}})
    if isinstance(project.get("project"), dict):
        out["project"].update({k: str(v) for k, v in project["project"].items() if k in {"name", "question"}})
    if isinstance(project.get("stages"), dict):
        for stage in STAGE_NAMES:
            value = project["stages"].get(stage, {})
            if isinstance(value, dict):
                status = value.get("status", "Not started")
                out["stages"][stage]["status"] = status if status in STATUS_VALUES else "Not started"
                out["stages"][stage]["notes"] = str(value.get("notes", ""))
                outputs = value.get("outputs", [])
                out["stages"][stage]["outputs"] = outputs if isinstance(outputs, list) else []
    out["artifacts"] = project.get("artifacts", []) if isinstance(project.get("artifacts"), list) else []
    out["links"] = project.get("links", []) if isinstance(project.get("links"), list) else []
    out["updated_at"] = datetime.now(timezone.utc).isoformat()
    return out


def set_stage(project: dict[str, Any], stage: str, status: str | None = None, notes: str | None = None, output: str | None = None) -> dict[str, Any]:
    out = normalize_project(project)
    if stage not in STAGE_NAMES:
        raise ValueError(f"Unknown research stage: {stage}")
    if status is not None:
        if status not in STATUS_VALUES:
            raise ValueError(f"Unknown status: {status}")
        out["stages"][stage]["status"] = status
    if notes is not None:
        out["stages"][stage]["notes"] = notes.strip()
    if output:
        out["stages"][stage]["outputs"].append(str(output).strip())
    out["updated_at"] = datetime.now(timezone.utc).isoformat()
    return out


def add_artifact(project: dict[str, Any], title: str, artifact_type: str, stage: str, source: str = "", description: str = "") -> dict[str, Any]:
    out = normalize_project(project)
    if stage not in STAGE_NAMES:
        raise ValueError(f"Unknown research stage: {stage}")
    clean = title.strip()
    if not clean:
        raise ValueError("Artifact title is required")
    artifact = {
        "id": f"artifact-{len(out['artifacts']) + 1:04d}",
        "title": clean,
        "type": artifact_type.strip() or "Other",
        "stage": stage,
        "source": source.strip(),
        "description": description.strip(),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    out["artifacts"].append(artifact)
    out["stages"][stage]["outputs"].append(clean)
    out["updated_at"] = artifact["created_at"]
    return out


def progress(project: dict[str, Any]) -> dict[str, int]:
    p = normalize_project(project)
    statuses = [p["stages"][stage]["status"] for stage in STAGE_NAMES]
    return {
        "total": len(STAGE_NAMES),
        "complete": statuses.count("Complete"),
        "ready": statuses.count("Ready"),
        "blocked": statuses.count("Blocked"),
        "in_progress": statuses.count("In progress"),
    }


def to_json(project: dict[str, Any]) -> str:
    return json.dumps(normalize_project(project), indent=2, ensure_ascii=False)


def from_json(text: str) -> dict[str, Any]:
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError("Invalid Research OS project JSON") from exc
    return normalize_project(value)
