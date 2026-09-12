"""Phase 116: authenticated Research OS access and project isolation.

This module centralizes the boundary used by Research OS cloud features. It
never trusts a project ID supplied by the browser: the authenticated Supabase
user is the source of ownership truth, and only projects returned for that
user are exposed to the UI.
"""
from __future__ import annotations

from typing import Any

from .cloud import configured, client, current_user, list_projects


def access_status(secrets: Any) -> dict[str, Any]:
    """Return safe authentication state without exposing credentials."""
    if not configured(secrets):
        return {"configured": False, "authenticated": False, "ready": False,
                "user_id": "", "reason": "Supabase cloud mode is not configured."}
    try:
        supa = client(secrets)
        user = current_user(supa)
        user_id = str(getattr(user, "id", "") or "") if user else ""
        return {"configured": True, "authenticated": bool(user_id), "ready": bool(user_id),
                "user_id": user_id,
                "reason": "Authenticated Research OS access is available." if user_id
                else "Sign in before accessing cloud project data."}
    except Exception as exc:
        return {"configured": True, "authenticated": False, "ready": False,
                "user_id": "", "reason": f"Authentication check failed: {exc}"}


def owned_projects(secrets: Any) -> list[dict[str, Any]]:
    """Return only projects owned by the current authenticated user."""
    status = access_status(secrets)
    if not status["ready"]:
        return []
    supa = client(secrets)
    return list_projects(supa, status["user_id"])


def owned_project_ids(secrets: Any) -> set[str]:
    return {str(p.get("id", "")) for p in owned_projects(secrets) if p.get("id")}


def authorize_project(secrets: Any, project_id: str) -> dict[str, Any]:
    """Authorize a project against the authenticated user's ownership list."""
    clean = str(project_id or "").strip()
    status = access_status(secrets)
    if not status["ready"]:
        return {"authorized": False, "project_id": clean, "reason": status["reason"], **status}
    projects = owned_projects(secrets)
    match = next((p for p in projects if str(p.get("id", "")) == clean), None)
    if match is None:
        return {"authorized": False, "project_id": clean,
                "reason": "Project is not accessible to the authenticated user.",
                "available_project_count": len(projects), **status}
    return {"authorized": True, "project_id": clean, "project": match,
            "reason": "Project ownership verified for the authenticated user.",
            "available_project_count": len(projects), **status}


def project_choices(secrets: Any) -> list[tuple[str, str]]:
    """UI-safe (id, label) choices from owned projects only."""
    rows = owned_projects(secrets)
    return [(str(p.get("id", "")), str(p.get("name", "Untitled project")))
            for p in rows if p.get("id")]


def isolation_audit(secrets: Any, requested_project_id: str = "") -> dict[str, Any]:
    """Produce a non-secret audit suitable for the Research OS UI."""
    status = access_status(secrets)
    result = {"configured": status["configured"], "authenticated": status["authenticated"],
              "user_bound": bool(status["user_id"]), "requested_project_id": str(requested_project_id or ""),
              "authorized": False, "project_count": 0, "healthy": False,
              "reason": status["reason"]}
    if not status["ready"]:
        return result
    try:
        projects = owned_projects(secrets)
        result["project_count"] = len(projects)
        if requested_project_id:
            result["authorized"] = str(requested_project_id) in {str(p.get("id", "")) for p in projects}
            result["reason"] = ("Requested project is owned by the authenticated user." if result["authorized"]
                                else "Requested project is not owned by the authenticated user.")
        else:
            result["authorized"] = True
            result["reason"] = "Authenticated user boundary is active; no project requested."
        result["healthy"] = True
    except Exception as exc:
        result["reason"] = f"Project isolation audit failed: {exc}"
    return result
