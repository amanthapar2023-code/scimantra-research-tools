import streamlit as st
import pandas as pd
from src.scimantra.research_workspace import workspace_snapshot, workspace_metrics, workspace_actions, export_workspace

st.set_page_config(page_title="Research Workspace | SciMantra", page_icon="🧠", layout="wide")
st.title("🧠 SciMantra Research Workspace")
st.caption("One project view connecting literature, evidence, methodology, results, claims, review, reproducibility, decisions, and research memory.")

snapshot = workspace_snapshot(st.session_state)
metrics = workspace_metrics(snapshot)

c1, c2, c3 = st.columns(3)
c1.metric("Pipeline modules", metrics["modules"])
c2.metric("Connected modules", metrics["active"])
c3.metric("Workspace coverage", f"{metrics['coverage']}%")

if snapshot.get("project_title"):
    st.success(f"Project: {snapshot['project_title']}")
else:
    st.info("No research title is connected yet. Start in Research Intelligence, then return here to see the project pipeline.")

st.subheader("Pipeline status")
rows = []
for name, info in snapshot["modules"].items():
    rows.append({"Module": name, "Status": "ACTIVE" if info.get("present") else "NOT CONNECTED", "Items": info.get("items", 0), "Detail": info.get("detail", "")})
st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

st.subheader("🔗 Next connections")
actions = workspace_actions(snapshot)
if actions:
    for action in actions:
        st.warning(action)
else:
    st.success("No structural connection gaps detected in the current session.")

st.subheader("Export project snapshot")
col1, col2 = st.columns(2)
col1.download_button("⬇️ Download Markdown snapshot", export_workspace(snapshot, "markdown"), "scimantra_research_workspace.md", "text/markdown", width="stretch")
col2.download_button("⬇️ Download JSON snapshot", export_workspace(snapshot, "json"), "scimantra_research_workspace.json", "application/json", width="stretch")

st.info("This workspace measures structural connectivity only. An ACTIVE module means relevant session data exists; it does not certify scientific validity, correctness, novelty, or reproducibility.")
