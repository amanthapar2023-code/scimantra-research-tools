"""Optional Supabase integration for SciMantra.

The app remains usable without Supabase configuration. When configured,
these helpers provide authenticated profile/project/subscription persistence.
The Supabase client uses the publishable/anon key only; privileged billing
webhook updates must happen in a trusted backend with a service role.
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


def subscription(supa, user_id: str) -> dict[str, Any]:
    result = supa.table("subscriptions").select("*").eq("user_id", user_id).maybe_single().execute()
    return result.data or {"user_id": user_id, "plan": "free", "status": "active", "provider": "none"}
