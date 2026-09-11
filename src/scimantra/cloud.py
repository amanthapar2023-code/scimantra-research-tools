"""Optional Supabase integration for SciMantra.

The app remains usable without Supabase configuration. When configured,
these helpers provide authenticated profile/project/subscription persistence
plus project-level research metadata.
"""

from __future__ import annotations

from typing import Any

try:
    from supabase import create_client
except ImportError:  # pragma: no cover - optional dependency
    create_client = None


def configured(secrets: Any) -> bool:
    try:
        return bool(secrets.get("SUPABASE_URL")) and bool(secrets.get("SUPABASE_ANON_KEY")) and create_client is not None
    except Exception:
        return False


def client(secrets: Any):
    if not configured(secrets):
        return None
    return create_client(secrets["SUPABASE_URL"], secrets["SUPABASE_ANON_KEY"])


def sign_up(supa, email: str, password: str, full_name: str = ""):
    return supa.auth.sign_up({"email": email, "password": password, "options": {"data": {"full_name": full_name}}})


def sign_in(supa, email: str, password: str):
    return supa.auth.sign_in_with_password({"email": email, "password": password})


def sign_out(supa) -> None:
    supa.auth.sign_out()


def current_user(supa):
    try:
        return supa.auth.get_user().user
    except Exception:
        return None


def load_profile(supa, user_id: str) -> dict[str, Any]:
    result = supa.table("profiles").select("*").eq("id", user_id).maybe_single().execute()
    return result.data or {"id": user_id, "full_name": "", "institution": "", "avatar_url": ""}


def save_profile(supa, user_id: str, full_name: str, institution: str, avatar_url: str = ""):
    return supa.table("profiles").upsert({"id": user_id, "full_name": full_name, "institution": institution, "avatar_url": avatar_url}).execute()


def list_projects(supa, user_id: str):
    return supa.table("projects").select("*").eq("owner_id", user_id).order("updated_at", desc=True).execute().data or []


def create_project(supa, user_id: str, name: str, status: str = "Planning", objective: str = ""):
    result = supa.table("projects").insert({"owner_id": user_id, "name": name, "status": status, "objective": objective}).execute()
    return result.data[0] if result.data else None


def save_project(supa, project: dict[str, Any]):
    return supa.table("projects").update({"name": project["name"], "status": project["status"], "objective": project.get("objective", ""), "notes": project.get("notes", "")}).eq("id", project["id"]).execute()


def list_project_datasets(supa, project_id: str):
    return supa.table("datasets").select("*").eq("project_id", project_id).order("created_at", desc=True).execute().data or []


def register_dataset(supa, user_id: str, project_id: str, name: str, storage_path: str = "", row_count: int = 0, column_count: int = 0):
    result = supa.table("datasets").insert({"project_id": project_id, "owner_id": user_id, "name": name, "storage_path": storage_path, "row_count": int(row_count), "column_count": int(column_count)}).execute()
    return result.data[0] if result.data else None


def list_experiments(supa, project_id: str):
    return supa.table("experiments").select("*").eq("project_id", project_id).order("created_at", desc=True).execute().data or []


def create_experiment(supa, user_id: str, project_id: str, name: str, design: str = "", outcome: str = "", status: str = "Planned"):
    result = supa.table("experiments").insert({"project_id": project_id, "owner_id": user_id, "name": name, "design": design, "outcome": outcome, "status": status}).execute()
    return result.data[0] if result.data else None


def list_milestones(supa, project_id: str):
    return supa.table("milestones").select("*").eq("project_id", project_id).order("due_date", desc=False).execute().data or []


def create_milestone(supa, user_id: str, project_id: str, title: str, due_date: str | None = None):
    result = supa.table("milestones").insert({"project_id": project_id, "owner_id": user_id, "title": title, "due_date": due_date}).execute()
    return result.data[0] if result.data else None


def set_milestone_completed(supa, milestone_id: str, completed: bool):
    return supa.table("milestones").update({"completed": bool(completed)}).eq("id", milestone_id).execute()


def subscription(supa, user_id: str) -> dict[str, Any]:
    result = supa.table("subscriptions").select("*").eq("user_id", user_id).maybe_single().execute()
    return result.data or {"user_id": user_id, "plan": "free", "status": "active", "provider": "none"}
