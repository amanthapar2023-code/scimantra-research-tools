"""Phase 116 — Research OS authentication & project isolation."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from scimantra.research_os_access import access_status, isolation_audit, owned_projects, authorize_project

st.set_page_config(page_title="SciMantra — Research OS Access", page_icon="🔐", layout="wide")
st.title("🔐 Phase 116 — Authentication & Project Isolation")
st.caption("Production access boundary for Research OS cloud data")
st.info("Cloud project data is exposed only after authentication. Project IDs are checked against the authenticated user's owned projects before cloud operations are permitted.")

secrets = st.secrets
status = access_status(secrets)

c1, c2, c3 = st.columns(3)
c1.metric("Cloud configured", "Yes" if status["configured"] else "No")
c2.metric("Authenticated", "Yes" if status["authenticated"] else "No")

projects = owned_projects(secrets)
c3.metric("Owned projects", len(projects))

if status["ready"]:
    st.success(status["reason"])
    st.caption(f"Authenticated user: `{status['user_id']}`")
else:
    st.warning(status["reason"])

st.divider()
st.subheader("🛡️ Project authorization check")
project_options = [(str(p.get("id")), str(p.get("name", "Untitled project"))) for p in projects if p.get("id")]
if project_options:
    labels = [f"{name} · {pid}" for pid, name in project_options]
    selected_label = st.selectbox("Select an owned project", labels)
    selected_id = project_options[labels.index(selected_label)][0]
else:
    selected_id = st.text_input("Project ID to audit", placeholder="Available after authentication")

check = authorize_project(secrets, selected_id)
if check.get("authorized"):
    st.success(check["reason"])
    project = check.get("project") or {}
    st.json({"id": project.get("id"), "name": project.get("name"), "owner_id": project.get("owner_id"), "status": project.get("status")})
elif selected_id:
    st.error(check["reason"])

st.subheader("📋 Owned project boundary")
if projects:
    st.dataframe(pd.DataFrame([
        {"project_id": p.get("id", ""), "name": p.get("name", ""), "owner_id": p.get("owner_id", ""), "status": p.get("status", "")}
        for p in projects
    ]), use_container_width=True, hide_index=True)
else:
    st.info("No owned projects are available in the authenticated session.")

st.subheader("🔎 Isolation audit")
audit = isolation_audit(secrets, selected_id)
a, b, c, d = st.columns(4)
a.metric("User bound", "Yes" if audit["user_bound"] else "No")
b.metric("Project boundary", "Verified" if audit["authorized"] else "Not verified")
c.metric("Owned projects", audit["project_count"])
d.metric("Audit", "Healthy" if audit["healthy"] else "Attention")
st.json(audit)

st.divider()
st.subheader("Production rules")
for rule in [
    "Authentication is required for Research OS cloud access.",
    "The authenticated user's ID is the ownership boundary; browser-supplied user IDs are never trusted.",
    "Project selectors expose only projects returned for the authenticated user.",
    "An unknown or foreign project ID is denied before Research OS cloud operations.",
    "No service-role key, password, session token, or secret is displayed or stored by this page.",
    "This layer verifies access boundaries only; it does not grant or infer scientific permissions.",
]:
    st.write(f"✅ {rule}")

st.caption("Phase 116 strengthens application-level isolation while preserving the existing Supabase schema and authentication architecture. Database RLS remains the final enforcement layer.")
