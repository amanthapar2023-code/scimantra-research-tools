"""Phase 114 — Research OS cloud persistence inspector."""
from __future__ import annotations
import json
import streamlit as st
from scimantra.research_os_access import owned_projects
from scimantra.research_os_data_bus import ensure_bus, new_bus
from scimantra.research_os_persistence import cloud_status, persistence_audit, save_snapshot, list_snapshots

st.set_page_config(page_title="SciMantra — Research OS Cloud Persistence", page_icon="☁️", layout="wide")
st.title("☁️ Phase 114 — Research OS Cloud Persistence")
st.caption("Durable Research OS snapshots with Phase 116 authenticated project isolation.")
st.info("Cloud writes require authentication. The project selector below exposes only projects owned by the current authenticated user.")

secrets = st.secrets
status = cloud_status(secrets)
projects = owned_projects(secrets)
project_options = [(str(p.get("id", "")), str(p.get("name", "Untitled project"))) for p in projects if p.get("id")]

if status["ready"]:
    st.success(status["reason"])
else:
    st.warning(status["reason"])

if project_options:
    labels = [f"{name} · {pid}" for pid, name in project_options]
    selected = st.selectbox("Owned project", labels)
    project_id = project_options[labels.index(selected)][0]
else:
    project_id = ""
    st.info("No owned project is available in the authenticated session.")

audit = persistence_audit(secrets, project_id)
a,b,c = st.columns(3)
a.metric("Cloud configured", "Yes" if status["configured"] else "No")
b.metric("Authenticated", "Yes" if status["authenticated"] else "No")
c.metric("Saved snapshots", audit.get("snapshots", 0))

st.divider()
tab1, tab2, tab3 = st.tabs(["💾 Save Snapshot", "↩️ Restore / Inspect", "🔎 Persistence Audit"])
with tab1:
    st.subheader("Save current Research OS state")
    bus_text = st.text_area("Research OS bus JSON", json.dumps(new_bus(), indent=2), height=260)
    if st.button("☁️ Save snapshot", type="primary", disabled=not project_id):
        try:
            bus = ensure_bus(json.loads(bus_text))
            artifact = save_snapshot(secrets, project_id, bus)
            st.success("Research OS snapshot saved as a project artifact.")
            st.json(artifact)
        except Exception as exc:
            st.error(str(exc))
with tab2:
    rows = list_snapshots(secrets, project_id) if project_id else []
    if not rows:
        st.info("No accessible Research OS snapshots found for this project.")
    else:
        labels = [r["saved_at"] for r in rows]
        selected = st.selectbox("Snapshot", labels)
        item = rows[labels.index(selected)]
        st.json(item["bus"])
        st.download_button("⬇️ Export selected snapshot", json.dumps(item["bus"], indent=2, ensure_ascii=False), "research_os_snapshot.json", "application/json")
with tab3:
    st.json(audit)
    if audit.get("healthy"):
        st.success("Persistence path is reachable for this owned project.")
    elif status["ready"] and project_id:
        st.error(audit.get("reason", "Persistence audit failed."))

st.divider()
st.caption("Production boundary: project selection and persistence are authenticated and ownership-checked. Database RLS remains the final enforcement layer.")
