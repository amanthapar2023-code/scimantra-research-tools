import streamlit as st
import pandas as pd
from src.scimantra.research_decision import rank_actions, decision_summary, export_decisions

st.set_page_config(page_title="Research Decision Engine | SciMantra", page_icon="🧭", layout="wide")
st.title("🧭 Research Decision Engine")
st.caption("Turn research uncertainty into a ranked queue of what to investigate next.")

st.write("Rate each current risk/gap from 0 (none) to 100 (critical). These scores are researcher inputs, not AI judgments of scientific truth.")
labels = [
    ("Evidence gap", "evidence_gap"), ("Experimental-design risk", "design_risk"),
    ("Analysis/robustness risk", "analysis_risk"), ("Alternative-explanation risk", "alternative_risk"),
    ("Reproducibility gap", "reproducibility_gap"), ("Novelty uncertainty", "novelty_risk")]
vals = {}
for label, key in labels:
    vals[key] = st.slider(label, 0, 100, 20, key=key)

if st.button("🧭 Rank my next actions", type="primary"):
    st.session_state.decision_rows = rank_actions(**vals)

rows = st.session_state.get("decision_rows", [])
if rows:
    summary = decision_summary(rows)
    st.success(f"Top current priority: {summary['top_action']} ({summary['priority']:.1f}/100)")
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
    st.download_button("Download decision queue", export_decisions(rows), "research_decision_queue.md", "text/markdown")
else:
    st.info("Enter your current uncertainty levels to generate a prioritized research-action queue.")

st.warning("The engine prioritizes researcher-supplied risks. It does not claim that the highest score is objectively the most important scientific problem.")
