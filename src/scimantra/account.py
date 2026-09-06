"""Lightweight account/project persistence helpers for SciMantra.

This module deliberately does not store passwords or secrets. It provides a
session-safe project store that can later be replaced by a managed database
and authentication provider without changing the page-level data model.
"""

from __future__ import annotations

import copy
from datetime import datetime, timezone
from typing import Any


def new_project(name: str = "Untitled Research Project", owner: str = "") -> dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    return {
        "id": now.replace(":", "").replace("+00:00", "Z"),
        "name": name.strip() or "Untitled Research Project",
        "owner": owner.strip(),
        "created_at": now,
        "updated_at": now,
        "status": "Planning",
        "objective": "",
        "notes": "",
        "experiments": [],
        "datasets": [],
        "milestones": [],
    }


def touch(project: dict[str, Any]) -> dict[str, Any]:
    project = copy.deepcopy(project)
    project["updated_at"] = datetime.now(timezone.utc).isoformat()
    return project


def project_summary(project: dict[str, Any]) -> dict[str, Any]:
    milestones = project.get("milestones", [])
    return {
        "id": project.get("id", ""),
        "name": project.get("name", "Untitled Research Project"),
        "owner": project.get("owner", ""),
        "status": project.get("status", "Planning"),
        "experiments": len(project.get("experiments", [])),
        "datasets": len(project.get("datasets", [])),
        "milestones": len(milestones),
        "completed_milestones": sum(bool(x.get("done")) for x in milestones),
        "updated_at": project.get("updated_at", ""),
    }
