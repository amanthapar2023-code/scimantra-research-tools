"""Phase 114: durable Research OS persistence gateway.

Uses the existing SciMantra Supabase project/artifact infrastructure. No new
schema is required: Research OS snapshots are stored as immutable artifact
records with typed provenance. Cloud mode is optional; callers can fall back
to the in-session Research OS bus when it is unavailable.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
import json

from .cloud import configured, client, current_user, list_projects, list_artifacts, create_artifact
from .research_os_data_bus import ensure_bus

SNAPSHOT_TYPE = "Research OS Snapshot"
SNAPSHOT_KIND = "research_os_snapshot"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def cloud_status(secrets: Any) -> dict[str, Any]:
    if not configured(secrets):
        return {"configured": False, "authenticated": False, "ready": False,
                "reason": "Supabase cloud mode is not configured."}
    try:
        supa = client(secrets)
        user = current_user(supa)
        return {"configured": True, "authenticated": bool(user), "ready": bool(user),
                "user_id": getattr(user, "id", "") if user else "",
                "reason": "Ready for authenticated project persistence." if user
                else "Sign in before using cloud persistence."}
    except Exception as exc:
        return {"configured": True, "authenticated": False, "ready": False,
                "reason": f"Cloud connection unavailable: {exc}"}


def _owned_project(supa, user_id: str, project_id: str) -> bool:
    return any(str(p.get("id", "")) == str(project_id)
               and str(p.get("owner_id", "")) == str(user_id)
               for p in list_projects(supa, user_id))


def save_snapshot(secrets: Any, project_id: str, bus: dict[str, Any]) -> dict[str, Any]:
    supa = client(secrets)
    if supa is None:
        raise RuntimeError("Supabase cloud mode is not configured")
    user = current_user(supa)
    user_id = getattr(user, "id", "") if user else ""
    if not user_id:
        raise PermissionError("Authenticated user required")
    if not _owned_project(supa, user_id, project_id):
        raise PermissionError("Project is not owned by the authenticated user")

    normalized = ensure_bus(bus)
    snapshot = {"kind": SNAPSHOT_KIND, "schema_version": normalized.get("schema_version", 1),
                "saved_at": _now(), "project_id": project_id, "bus": normalized}
    body = json.dumps(snapshot, ensure_ascii=False, separators=(",", ":"))
    artifact = create_artifact(
        supa, user_id, project_id,
        f"Research OS Snapshot · {snapshot['saved_at']}",
        SNAPSHOT_TYPE, "", "application/json", len(body.encode("utf-8")),
        "", "Research OS", snapshot,
    )
    if not artifact:
        raise RuntimeError("Persistence returned no artifact record")
    return artifact


def list_snapshots(secrets: Any, project_id: str) -> list[dict[str, Any]]:
    supa = client(secrets)
    if supa is None:
        return []
    user = current_user(supa)
    user_id = getattr(user, "id", "") if user else ""
    if not user_id or not _owned_project(supa, user_id, project_id):
        return []

    rows = list_artifacts(supa, project_id)
    snapshots: list[dict[str, Any]] = []
    for row in rows:
        provenance = row.get("provenance_json") or {}
        if isinstance(provenance, str):
            try:
                provenance = json.loads(provenance)
            except Exception:
                provenance = {}
        if isinstance(provenance, dict) and provenance.get("kind") == SNAPSHOT_KIND and isinstance(provenance.get("bus"), dict):
            snapshots.append({"artifact": row, "saved_at": provenance.get("saved_at", row.get("created_at", "")),
                              "bus": ensure_bus(provenance["bus"])})
    snapshots.sort(key=lambda x: x.get("saved_at", ""), reverse=True)
    return snapshots


def load_latest_snapshot(secrets: Any, project_id: str) -> dict[str, Any] | None:
    rows = list_snapshots(secrets, project_id)
    return rows[0]["bus"] if rows else None


def persistence_audit(secrets: Any, project_id: str = "") -> dict[str, Any]:
    status = cloud_status(secrets)
    result = {**status, "project_id": project_id, "snapshots": 0, "latest_saved_at": ""}
    if not status["ready"] or not project_id:
        return result
    try:
        rows = list_snapshots(secrets, project_id)
        result["snapshots"] = len(rows)
        result["latest_saved_at"] = rows[0]["saved_at"] if rows else ""
        result["healthy"] = True
    except Exception as exc:
        result["healthy"] = False
        result["reason"] = str(exc)
    return result
