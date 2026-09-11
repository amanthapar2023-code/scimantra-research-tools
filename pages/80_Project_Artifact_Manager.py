"""SciMantra Research OS — Project Artifact Manager."""
import pandas as pd
import streamlit as st
from src.scimantra.project_artifact_manager import (
    ARTIFACT_STATUSES, ARTIFACT_TYPES, add_artifact, archive_artifact,
    audit_artifacts, ensure_manager, search_artifacts, summary, update_status,
)
from src.scimantra.research_os_state import STAGE_NAMES

st.set_page_config(page_title="Project Artifact Manager", page_icon="🗂️", layout="wide")

if "os_artifact_manager" not in st.session_state:
    st.session_state.os_artifact_manager = ensure_manager()
state = st.session_state.os_artifact_manager

st.title("🗂️ Project Artifact Manager")
st.caption("A single registry for the objects produced across the SciMantra Research OS.")
st.info("Artifacts are researcher-managed records. Registration or verification status does not certify scientific validity.")

s = summary(state)
m = st.columns(5)
m[0].metric("Artifacts", s["total"])
m[1].metric("Active", s["active"])
m[2].metric("Needs review", s["needs_review"])
m[3].metric("Verified", s["verified"])
m[4].metric("Archived", s["archived"])

st.divider()

left, right = st.columns([1.05, 1])
with left:
    st.subheader("➕ Register / update artifact")
    with st.form("artifact_manager_form"):
        c1, c2 = st.columns(2)
        artifact_id = c1.text_input("Artifact ID", placeholder="e.g., DATA-001")
        title = c2.text_input("Title", placeholder="e.g., VOC concentration dataset")
        c3, c4 = st.columns(2)
        artifact_type = c3.selectbox("Type", ARTIFACT_TYPES)
        stage = c4.selectbox("Research stage", STAGE_NAMES)
        c5, c6 = st.columns(2)
        status = c5.selectbox("Lifecycle status", ARTIFACT_STATUSES)
        location = c6.text_input("Location / file / DOI / URL")
        owner = st.text_input("Owner / contributor")
        tags = st.text_input("Tags", placeholder="VOC, BTEX, indoor-air, dataset")
        description = st.text_area("Description", placeholder="What is this artifact and why does it matter?")
        save = st.form_submit_button("Save artifact", type="primary", width="stretch")
    if save:
        try:
            tags_list = [x.strip() for x in tags.split(",") if x.strip()]
            state = add_artifact(state, artifact_id, title, artifact_type, stage, status, location, owner, tags_list, description)
            st.session_state.os_artifact_manager = state
            st.success(f"Saved artifact **{title.strip()}**.")
        except ValueError as exc:
            st.error(str(exc))

with right:
    st.subheader("🔎 Find artifacts")
    q = st.text_input("Search", placeholder="Search ID, title, tag, DOI, description…")
    f1, f2 = st.columns(2)
    type_filter = f1.selectbox("Type", ["All"] + ARTIFACT_TYPES)
    stage_filter = f2.selectbox("Stage", ["All"] + STAGE_NAMES)
    status_filter = st.selectbox("Status", ["All"] + ARTIFACT_STATUSES)
    results = search_artifacts(state, q, type_filter, stage_filter, status_filter)
    st.caption(f"{len(results)} matching artifact(s)")
    if results:
        st.dataframe(pd.DataFrame(results)[["id", "title", "type", "stage", "status", "location"]], use_container_width=True, hide_index=True)
    else:
        st.info("No matching artifacts.")

st.divider()
st.subheader("⚙️ Lifecycle management")
if state["artifacts"]:
    ids = [a.get("id", "") for a in state["artifacts"]]
    selected = st.selectbox("Select artifact", ids)
    selected_record = next(a for a in state["artifacts"] if a.get("id") == selected)
    c1, c2, c3 = st.columns(3)
    new_status = c1.selectbox("Change status", ARTIFACT_STATUSES, index=ARTIFACT_STATUSES.index(selected_record.get("status", "Draft")))
    if c2.button("Update status", width="stretch"):
        try:
            state = update_status(state, selected, new_status)
            st.session_state.os_artifact_manager = state
            st.rerun()
        except ValueError as exc:
            st.error(str(exc))
    if c3.button("Archive artifact", width="stretch"):
        state = archive_artifact(state, selected)
        st.session_state.os_artifact_manager = state
        st.rerun()
else:
    st.info("Register your first project artifact above.")

st.divider()
st.subheader("🛡️ Artifact quality audit")
a = audit_artifacts(state)
q1, q2, q3, q4 = st.columns(4)
q1.metric("Duplicate IDs", len(a["duplicate_ids"]))
q2.metric("Missing title", len(a["missing_title"]))
q3.metric("Missing stage", len(a["missing_stage"]))
q4.metric("Needs review", len(a["needs_review"]))
if a["duplicate_ids"] or a["missing_title"] or a["missing_stage"]:
    st.warning("The registry contains metadata issues that should be corrected before relying on it as a project index.")
else:
    st.success("No duplicate IDs or missing title/stage fields detected.")

if state["artifacts"]:
    st.subheader("📋 Full registry")
    st.dataframe(pd.DataFrame(state["artifacts"]), use_container_width=True, hide_index=True)

st.caption("Module 80 · Project Artifact Manager · Decision support and project organization only.")
