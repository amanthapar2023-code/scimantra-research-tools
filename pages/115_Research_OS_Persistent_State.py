"""Phase 115 — Research OS persistent state and synchronization."""
import json
import streamlit as st

from scimantra.research_os_data_bus import ensure_bus
from scimantra.research_os_sync import (
    DEFAULT_AUTOSAVE_SECONDS,
    export_sync_state,
    ensure_sync_state,
    latest_cloud_metadata,
    load_cloud,
    mark_dirty,
    new_sync_state,
    save_cloud,
    sync_status,
)

st.set_page_config(page_title="Research OS Persistent State", page_icon="☁️", layout="wide")
st.title("☁️ Research OS — Persistent State & Sync")
st.caption("Phase 115 · session ↔ cloud synchronization without changing the existing database schema")

if "ros_bus" not in st.session_state:
    st.session_state.ros_bus = ensure_bus({})
if "ros_sync" not in st.session_state:
    st.session_state.ros_sync = new_sync_state()
st.session_state.ros_sync = ensure_sync_state(st.session_state.ros_sync)

with st.sidebar:
    st.header("Project sync")
    project_id = st.text_input("Supabase project ID", st.session_state.ros_sync.get("project_id", ""))
    if project_id != st.session_state.ros_sync.get("project_id", ""):
        st.session_state.ros_sync = mark_dirty(st.session_state.ros_sync, project_id)
    autosave = st.checkbox("Enable autosave", value=st.session_state.ros_sync.get("autosave_enabled", False))
    interval = st.number_input("Autosave interval (seconds)", min_value=60, value=int(st.session_state.ros_sync.get("autosave_interval_seconds", DEFAULT_AUTOSAVE_SECONDS)), step=60)
    st.session_state.ros_sync["autosave_enabled"] = autosave
    st.session_state.ros_sync["autosave_interval_seconds"] = int(interval)

secrets = st.secrets
status = sync_status(secrets, st.session_state.ros_sync, project_id)
cloud = status.get("cloud", {})
cloud_snapshot = status.get("cloud_snapshot", {})

c1, c2, c3, c4 = st.columns(4)
c1.metric("Cloud", "Ready" if cloud.get("ready") else "Unavailable")
c2.metric("Local state", "Dirty" if st.session_state.ros_sync.get("dirty") else "Synced")
c3.metric("Snapshots", "Available" if cloud_snapshot.get("exists") else "None")
c4.metric("Conflict", "Resolve" if status.get("conflict") else "None")

if not cloud.get("ready"):
    st.warning(cloud.get("reason", "Cloud persistence is unavailable."))
else:
    st.success("Authenticated cloud persistence is available for this project.")

st.subheader("🔄 Synchronization controls")
a, b, c = st.columns(3)
with a:
    if st.button("☁️ Load latest cloud state", use_container_width=True):
        try:
            bus, new_state = load_cloud(secrets, st.session_state.ros_sync, project_id)
            if bus is None:
                st.info("No Research OS snapshot exists for this project yet.")
            else:
                st.session_state.ros_bus = bus
                st.session_state.ros_sync = new_state
                st.success("Latest cloud state loaded into the current session.")
        except Exception as exc:
            st.error(f"Cloud load failed: {exc}")
with b:
    if st.button("💾 Save local state now", use_container_width=True):
        try:
            artifact, new_state = save_cloud(secrets, st.session_state.ros_sync, project_id, st.session_state.ros_bus)
            st.session_state.ros_sync = new_state
            st.success(f"Saved Research OS snapshot: {artifact.get('id', 'created')}")
        except Exception as exc:
            st.error(f"Cloud save blocked: {exc}")
with c:
    if st.button("✏️ Mark local state dirty", use_container_width=True):
        st.session_state.ros_sync = mark_dirty(st.session_state.ros_sync, project_id)
        st.info("Local state marked as changed; it will not silently overwrite a newer cloud snapshot.")

if status.get("conflict"):
    st.error("⚠️ Conflict detected: the cloud snapshot is newer than the current unsaved local state. Load cloud state or review/merge the states before saving.")

st.subheader("📋 Sync state")
st.json(st.session_state.ros_sync)

st.subheader("☁️ Latest cloud snapshot")
if cloud_snapshot.get("exists"):
    st.write({k: cloud_snapshot.get(k) for k in ["saved_at", "artifact_id"]})
    with st.expander("Inspect cloud bus", expanded=False):
        st.json(cloud_snapshot.get("bus") or {})
else:
    st.info("No snapshot found for the selected project.")

st.subheader("🧪 Local Research OS bus")
st.caption("This is the canonical in-session bus used by the Research OS integration layer. Editing below is intentionally JSON-only and should be used for controlled recovery/import workflows.")
local_text = st.text_area("Local bus JSON", value=json.dumps(st.session_state.ros_bus, ensure_ascii=False, indent=2), height=300)
if st.button("Apply local bus JSON"):
    try:
        candidate = json.loads(local_text)
        st.session_state.ros_bus = ensure_bus(candidate)
        st.session_state.ros_sync = mark_dirty(st.session_state.ros_sync, project_id)
        st.success("Local bus updated and marked dirty.")
    except Exception as exc:
        st.error(f"Invalid bus JSON: {exc}")

st.subheader("🕘 Snapshot history")
if cloud.get("ready") and project_id:
    try:
        from scimantra.research_os_persistence import list_snapshots
        rows = list_snapshots(secrets, project_id)
        if rows:
            st.dataframe([{
                "saved_at": r.get("saved_at", ""),
                "artifact_id": (r.get("artifact") or {}).get("id", ""),
                "artifacts": len((r.get("bus") or {}).get("artifacts", {})),
                "events": len((r.get("bus") or {}).get("events", [])),
            } for r in rows], use_container_width=True, hide_index=True)
        else:
            st.info("No saved snapshots yet.")
    except Exception as exc:
        st.error(f"Snapshot history unavailable: {exc}")

with st.expander("Export synchronization metadata"):
    st.download_button("Download sync state JSON", export_sync_state(st.session_state.ros_sync), "research_os_sync_state.json", "application/json")

st.divider()
st.warning("Synchronization stores and restores researcher-controlled project state. It does not validate scientific correctness, resolve scientific disagreements automatically, or certify results. Autosave is represented as a safe configuration flag here; automatic background writes should be wired only after deployment-specific rerun/session behavior is verified.")
