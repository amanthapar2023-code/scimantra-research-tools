"""SciMantra Research OS — Automatic Analysis Pipeline."""
import pandas as pd
import streamlit as st
from src.scimantra.automatic_analysis_pipeline import STEPS, STATUSES, new_pipeline, audit, next_actions

st.set_page_config(page_title="Automatic Analysis Pipeline", page_icon="⚙️", layout="wide")
st.title("⚙️ Automatic Analysis Pipeline")
st.caption("A controlled route from registered dataset to analysis-ready result and publication output.")
st.warning("This module orchestrates and audits analysis workflow state. It does not automatically invent a statistical method, alter data, or certify scientific conclusions.")

if "analysis_pipeline" not in st.session_state:
    st.session_state.analysis_pipeline = new_pipeline(st.session_state.get("dataset_id", ""))
p = st.session_state.analysis_pipeline

c1,c2,c3 = st.columns(3)
p["dataset_id"] = c1.text_input("Dataset ID", value=p.get("dataset_id", ""))
p["analysis"] = c2.text_input("Analysis / method", value=p.get("analysis", ""), placeholder="e.g. ANOVA + post-hoc")
p["outcome"] = c3.text_input("Primary outcome", value=p.get("outcome", ""))

st.subheader("Pipeline status")
for i, step in enumerate(STEPS):
    left,right = st.columns([3,2])
    left.write(f"**{i+1}. {step}**")
    p["steps"][step] = right.selectbox(step, STATUSES, index=STATUSES.index(p["steps"].get(step,"Not started")), key=f"pipeline_{i}", label_visibility="collapsed")

p["notes"] = st.text_area("Analysis notes / rationale", value=p.get("notes", ""))
a = audit(p)
m1,m2,m3 = st.columns(3)
m1.metric("Completed", f'{a["complete_steps"]}/{a["total_steps"]}')
m2.metric("Blocked", len(a["blocked"]))
m3.metric("Ready for interpretation", "Yes" if a["ready_for_interpretation"] else "No")

st.subheader("Next actions")
for action in next_actions(p): st.write("→", action)

if a["issues"]:
    st.subheader("Audit findings")
    for issue in a["issues"]: st.warning(issue)
else:
    st.success("No structural workflow issues detected.")

st.subheader("Pipeline map")
map_df = pd.DataFrame({"Step": STEPS, "Status": [p["steps"].get(x,"Not started") for x in STEPS]})
st.dataframe(map_df, use_container_width=True, hide_index=True)
st.download_button("Download pipeline CSV", map_df.to_csv(index=False), "scimantra_analysis_pipeline.csv", "text/csv")
st.caption("Module 86 · Analysis orchestration layer · researcher-controlled execution.")
