"""Phase 114 — Research OS cloud persistence inspector."""
from __future__ import annotations
import json
import streamlit as st
from scimantra.research_os_data_bus import ensure_bus, new_bus
from scimantra.research_os_persistence import cloud_status, persistence_audit, save_snapshot, list_snapshots

st.set_page_config(page_title="SciMantra — Research OS Cloud Persistence", page_icon="☁️", layout="wide")
st.title("☁️ Phase 114 — Research OS Cloud Persistence")
st.caption("Durable Research OS snapshots using SciMantra's existing authenticated Supabase project/artifact infrastructure.")
st.info("This phase adds persistence without creating a second database or changing scientific calculations. Cloud writes require an authenticated user who owns the selected project.")

secrets = st.secrets
status = cloud_status(secrets)
if status["ready"]:
    st.success(status["reason"])
else:
    st.warning(status["reason"])

project_id = st.text_input("Project ID", placeholder="Your existing Supabase project ID")
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
    if st.button("☁️ Save snapshot", type="primary"):
        try:
            bus = ensure_bus(json.loads(bus_text))
            artifact = save_snapshot(secrets, project_id.strip(), bus)
            st.success("Research OS snapshot saved as a project artifact.")
            st.json(artifact)
        except Exception as exc:
            st.error(str(exc))
with tab2:
    rows = list_snapshots(secrets, project_id.strip()) if project_id.strip() else []
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
        st.success("Persistence path is reachable for this project.")
    elif status["ready"] and project_id:
        st.error(audit.get("reason", "Persistence audit failed."))

st.divider()
st.caption("Production boundary: snapshots are project-scoped and ownership-checked. Persistence does not certify scientific validity, modify research results, or replace the existing artifact model.")
