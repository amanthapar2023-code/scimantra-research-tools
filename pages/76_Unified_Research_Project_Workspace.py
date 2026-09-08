import pandas as pd
import streamlit as st
from src.scimantra.research_project_workspace import template, audit, next_steps, export_workspace, STATUSES

st.set_page_config(page_title="Unified Research Project Workspace | SciMantra", page_icon="🗂️", layout="wide")
st.title("🗂️ Unified Research Project Workspace")
st.caption("One project map from research question to submission readiness.")
st.warning("Integrity rule: completion tracks workflow organization only. It does not certify scientific validity, reproducibility, or publication readiness.")

if "workspace_rows" not in st.session_state:
    st.session_state.workspace_rows = template()

project = st.text_input("Project title", placeholder="e.g., Biological treatment of H₂S in wastewater")
objective = st.text_area("Central research objective / question", placeholder="What exactly is this project trying to establish?", height=90)

st.subheader("Research workflow")
for i, row in enumerate(st.session_state.workspace_rows):
    with st.expander(f"{row['ID']}. {row['Stage']} — {row['Status']}", expanded=i == 0):
        row["Status"] = st.selectbox("Stage status", STATUSES, index=STATUSES.index(row.get("Status", "Not started")), key=f"ws_status_{i}")
        row["Evidence / artifact"] = st.text_input("Evidence / artifact / module output", row.get("Evidence / artifact", ""), key=f"ws_artifact_{i}")
        row["Owner / note"] = st.text_area("Owner / note / next decision", row.get("Owner / note", ""), key=f"ws_note_{i}")

if st.button("🗂️ Build project map", type="primary", use_container_width=True):
    st.session_state.workspace_summary = audit(st.session_state.workspace_rows)

summary = st.session_state.get("workspace_summary")
if summary:
    st.divider()
    st.subheader("Project dashboard")
    a,b,c,d = st.columns(4)
    a.metric("Workflow completion", f"{summary['completion']}%")
    b.metric("Complete", summary["counts"]["Complete"])
    c.metric("Needs attention", summary["counts"]["Needs attention"])
    d.metric("In progress", summary["counts"]["In progress"])
    if summary["attention"]:
        st.warning("**Attention:** " + ", ".join(summary["attention"]))
    elif summary["completion"] == 100:
        st.success("All workflow stages are marked complete. Continue with your independent scientific and journal-specific checks.")
    else:
        st.info("Keep advancing the earliest incomplete stage while preserving its evidence/artifact link.")

    st.subheader("Next-action queue")
    st.dataframe(pd.DataFrame(next_steps(st.session_state.workspace_rows)), use_container_width=True, hide_index=True)
    st.subheader("Project map")
    st.dataframe(pd.DataFrame(st.session_state.workspace_rows), use_container_width=True, hide_index=True)
    st.download_button("⬇️ Export project workspace", export_workspace(st.session_state.workspace_rows, summary), "scimantra_unified_research_workspace.md", "text/markdown", use_container_width=True)
else:
    st.info("Complete the stage statuses and select **Build project map** to calculate workflow progress.")

st.subheader("How this becomes the SciMantra research operating system")
st.write("**Question → Literature → Hypothesis → Experiment → Data → Analysis → Evidence → Claims → Manuscript → Peer review → Readiness**")
st.caption("The workspace is intentionally modular: individual SciMantra audit tools can be used at each stage and their outputs can be recorded here as project evidence.")
