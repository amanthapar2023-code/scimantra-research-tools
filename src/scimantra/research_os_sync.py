"""Phase 115: session/cloud synchronization for the Research OS.

Keeps synchronization explicit and conflict-safe. This module does not change
Supabase schema and never treats synchronization as scientific validation.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
import json

from .research_os_data_bus import ensure_bus
from .research_os_persistence import cloud_status, list_snapshots, load_latest_snapshot, save_snapshot

SYNC_SCHEMA_VERSION = 1
DEFAULT_AUTOSAVE_SECONDS = 300


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_sync_state(project_id: str = "", bus: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "schema_version": SYNC_SCHEMA_VERSION,
        "project_id": project_id,
        "dirty": bool(bus),
        "last_synced_at": "",
        "last_cloud_saved_at": "",
        "last_cloud_loaded_at": "",
        "last_local_change_at": now() if bus else "",
        "source": "session" if bus else "none",
        "conflict": False,
        "autosave_enabled": False,
        "autosave_interval_seconds": DEFAULT_AUTOSAVE_SECONDS,
    }


def ensure_sync_state(state: dict[str, Any] | None) -> dict[str, Any]:
    base = new_sync_state()
    if isinstance(state, dict):
        base.update(state)
    base["schema_version"] = SYNC_SCHEMA_VERSION
    base["project_id"] = str(base.get("project_id", ""))
    base["dirty"] = bool(base.get("dirty", False))
    base["conflict"] = bool(base.get("conflict", False))
    base["autosave_enabled"] = bool(base.get("autosave_enabled", False))
    try:
        base["autosave_interval_seconds"] = max(60, int(base.get("autosave_interval_seconds", DEFAULT_AUTOSAVE_SECONDS)))
    except (TypeError, ValueError):
        base["autosave_interval_seconds"] = DEFAULT_AUTOSAVE_SECONDS
    return base


def mark_dirty(state: dict[str, Any], project_id: str | None = None) -> dict[str, Any]:
    state = ensure_sync_state(state)
    if project_id is not None:
        state["project_id"] = str(project_id)
    state["dirty"] = True
    state["source"] = "session"
    state["last_local_change_at"] = now()
    return state


def mark_synced(state: dict[str, Any], saved_at: str = "", source: str = "cloud") -> dict[str, Any]:
    state = ensure_sync_state(state)
    stamp = saved_at or now()
    state["dirty"] = False
    state["conflict"] = False
    state["source"] = source
    state["last_synced_at"] = stamp
    if source == "cloud":
        state["last_cloud_saved_at"] = stamp
    return state


def latest_cloud_metadata(secrets: Any, project_id: str) -> dict[str, Any]:
    rows = list_snapshots(secrets, project_id) if project_id else []
    if not rows:
        return {"exists": False, "saved_at": "", "artifact_id": "", "bus": None}
    row = rows[0]
    artifact = row.get("artifact") or {}
    return {
        "exists": True,
        "saved_at": str(row.get("saved_at", "")),
        "artifact_id": str(artifact.get("id", "")),
        "bus": ensure_bus(row.get("bus") or {}),
    }


def sync_status(secrets: Any, state: dict[str, Any], project_id: str = "") -> dict[str, Any]:
    state = ensure_sync_state(state)
    pid = project_id or state.get("project_id", "")
    status = cloud_status(secrets)
    result = {**state, "project_id": pid, "cloud": status, "cloud_snapshot": {"exists": False}}
    if status.get("ready") and pid:
        try:
            result["cloud_snapshot"] = latest_cloud_metadata(secrets, pid)
            cloud_at = result["cloud_snapshot"].get("saved_at", "")
            local_at = state.get("last_local_change_at", "")
            result["conflict"] = bool(state.get("dirty") and cloud_at and local_at and cloud_at > local_at)
        except Exception as exc:
            result["cloud_error"] = str(exc)
    return result


def load_cloud(secrets: Any, state: dict[str, Any], project_id: str) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    state = ensure_sync_state(state)
    bus = load_latest_snapshot(secrets, project_id)
    if bus is None:
        state["project_id"] = project_id
        state["last_cloud_loaded_at"] = now()
        state["source"] = "cloud"
        return None, state
    metadata = latest_cloud_metadata(secrets, project_id)
    stamp = metadata.get("saved_at") or now()
    state["project_id"] = project_id
    state["dirty"] = False
    state["conflict"] = False
    state["source"] = "cloud"
    state["last_synced_at"] = stamp
    state["last_cloud_loaded_at"] = stamp
    state["last_cloud_saved_at"] = stamp
    return ensure_bus(bus), state


def save_cloud(secrets: Any, state: dict[str, Any], project_id: str, bus: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    state = ensure_sync_state(state)
    if not project_id:
        raise ValueError("Project ID is required for cloud synchronization")
    status = sync_status(secrets, state, project_id)
    if status.get("conflict"):
        raise RuntimeError("Cloud snapshot is newer than the unsaved local state; resolve the conflict before saving.")
    artifact = save_snapshot(secrets, project_id, ensure_bus(bus))
    saved_at = str(artifact.get("created_at", "")) or now()
    state["project_id"] = project_id
    state = mark_synced(state, saved_at=saved_at, source="cloud")
    return artifact, state


def conflict_summary(secrets: Any, state: dict[str, Any], project_id: str) -> dict[str, Any]:
    status = sync_status(secrets, state, project_id)
    cloud_snapshot = status.get("cloud_snapshot", {})
    return {
        "conflict": bool(status.get("conflict")),
        "project_id": project_id,
        "local_dirty": bool(state.get("dirty")),
        "local_changed_at": state.get("last_local_change_at", ""),
        "last_synced_at": state.get("last_synced_at", ""),
        "cloud_saved_at": cloud_snapshot.get("saved_at", ""),
        "cloud_artifact_id": cloud_snapshot.get("artifact_id", ""),
        "resolution_required": bool(status.get("conflict")),
    }


def export_sync_state(state: dict[str, Any]) -> str:
    return json.dumps(ensure_sync_state(state), ensure_ascii=False, indent=2)
