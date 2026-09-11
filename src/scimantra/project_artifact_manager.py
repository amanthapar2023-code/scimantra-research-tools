"""Project artifact management for the SciMantra Research OS.

Artifacts are researcher-owned project objects. The manager provides indexing,
filtering, validation and lifecycle operations without claiming scientific truth.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

ARTIFACT_TYPES = [
    "Question", "Hypothesis", "Literature", "Dataset", "Protocol", "Analysis",
    "Result", "Figure", "Table", "Claim", "Manuscript", "Review", "Other",
]
ARTIFACT_STATUSES = ["Draft", "Active", "Needs review", "Verified", "Archived"]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_manager(state: dict[str, Any] | None = None) -> dict[str, Any]:
    if not isinstance(state, dict):
        state = {}
    return {
        "schema_version": 1,
        "artifacts": list(state.get("artifacts", [])) if isinstance(state.get("artifacts"), list) else [],
        "updated_at": _now(),
    }


def add_artifact(state: dict[str, Any], artifact_id: str, title: str, artifact_type: str, stage: str,
                 status: str = "Draft", location: str = "", owner: str = "", tags: list[str] | None = None,
                 description: str = "") -> dict[str, Any]:
    out = ensure_manager(state)
    artifact_id, title = artifact_id.strip(), title.strip()
    if not artifact_id or not title:
        raise ValueError("Artifact ID and title are required")
    if artifact_type not in ARTIFACT_TYPES:
        raise ValueError(f"Unsupported artifact type: {artifact_type}")
    if status not in ARTIFACT_STATUSES:
        raise ValueError(f"Unsupported artifact status: {status}")
    record = {
        "id": artifact_id, "title": title, "type": artifact_type, "stage": stage.strip(),
        "status": status, "location": location.strip(), "owner": owner.strip(),
        "tags": [str(x).strip() for x in (tags or []) if str(x).strip()],
        "description": description.strip(), "updated_at": _now(),
    }
    existing = next((a for a in out["artifacts"] if a.get("id") == artifact_id), None)
    if existing is None:
        record["created_at"] = record["updated_at"]
        out["artifacts"].append(record)
    else:
        record["created_at"] = existing.get("created_at", record["updated_at"])
        existing.update(record)
    out["updated_at"] = record["updated_at"]
    return out


def update_status(state: dict[str, Any], artifact_id: str, status: str) -> dict[str, Any]:
    out = ensure_manager(state)
    if status not in ARTIFACT_STATUSES:
        raise ValueError(f"Unsupported artifact status: {status}")
    for artifact in out["artifacts"]:
        if artifact.get("id") == artifact_id:
            artifact["status"] = status
            artifact["updated_at"] = _now()
            out["updated_at"] = artifact["updated_at"]
            return out
    raise ValueError(f"Unknown artifact: {artifact_id}")


def archive_artifact(state: dict[str, Any], artifact_id: str) -> dict[str, Any]:
    return update_status(state, artifact_id, "Archived")


def search_artifacts(state: dict[str, Any], query: str = "", artifact_type: str = "All",
                     stage: str = "All", status: str = "All") -> list[dict[str, Any]]:
    q = query.strip().lower()
    out = []
    for a in ensure_manager(state)["artifacts"]:
        if artifact_type != "All" and a.get("type") != artifact_type:
            continue
        if stage != "All" and a.get("stage") != stage:
            continue
        if status != "All" and a.get("status") != status:
            continue
        haystack = " ".join(str(a.get(k, "")) for k in ["id", "title", "description", "location", "owner", "stage", "type", "tags"]).lower()
        if q and q not in haystack:
            continue
        out.append(a)
    return sorted(out, key=lambda x: x.get("updated_at", ""), reverse=True)


def audit_artifacts(state: dict[str, Any]) -> dict[str, Any]:
    artifacts = ensure_manager(state)["artifacts"]
    ids = [a.get("id") for a in artifacts]
    duplicate_ids = sorted({x for x in ids if x and ids.count(x) > 1})
    missing_title = [a.get("id") for a in artifacts if not str(a.get("title", "")).strip()]
    missing_stage = [a.get("id") for a in artifacts if not str(a.get("stage", "")).strip()]
    missing_location = [a.get("id") for a in artifacts if not str(a.get("location", "")).strip()]
    review = [a.get("id") for a in artifacts if a.get("status") == "Needs review"]
    return {
        "total": len(artifacts), "duplicate_ids": duplicate_ids,
        "missing_title": missing_title, "missing_stage": missing_stage,
        "missing_location": missing_location, "needs_review": review,
        "archived": sum(a.get("status") == "Archived" for a in artifacts),
    }


def summary(state: dict[str, Any]) -> dict[str, Any]:
    artifacts = ensure_manager(state)["artifacts"]
    return {
        "total": len(artifacts),
        "active": sum(a.get("status") == "Active" for a in artifacts),
        "draft": sum(a.get("status") == "Draft" for a in artifacts),
        "needs_review": sum(a.get("status") == "Needs review" for a in artifacts),
        "verified": sum(a.get("status") == "Verified" for a in artifacts),
        "archived": sum(a.get("status") == "Archived" for a in artifacts),
    }
