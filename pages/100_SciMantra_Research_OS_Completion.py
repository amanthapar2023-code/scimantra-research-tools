"""SciMantra Research OS — Module 100 integration milestone."""
import pandas as pd
import streamlit as st
from src.scimantra.research_os_completion import integration_snapshot,completion_report

st.set_page_config(page_title="SciMantra Research OS",page_icon="🧠",layout="wide")
st.title("🧠 SciMantra Research OS")
st.subheader("Module 100 — Integration Milestone")
st.caption("A single architecture connecting the research lifecycle, scientific-audit layers and project infrastructure.")
st.success("The Module 100 architecture is assembled. The next phase is integration testing, wiring and production hardening — not simply adding more isolated modules.")

r=completion_report(); a,b,c=st.columns(3); a.metric("Workflow stages",r["workflow"]); b.metric("Intelligence layers",r["intelligence"]); c.metric("Infrastructure layers",r["infrastructure"])
s=integration_snapshot()

st.subheader("1 · Research lifecycle")
st.dataframe(pd.DataFrame({"Stage":s["workflow_stages"]}),use_container_width=True,hide_index=True)

st.subheader("2 · Scientific intelligence")
st.dataframe(pd.DataFrame({"Layer":s["intelligence_layers"]}),use_container_width=True,hide_index=True)

st.subheader("3 · Research infrastructure")
st.dataframe(pd.DataFrame({"Layer":s["infrastructure_layers"]}),use_container_width=True,hide_index=True)

st.subheader("What Module 100 means")
st.markdown("**Question → Literature → Hypothesis → Experiment → Data → Analysis → Evidence → Claims → Manuscript → Review → Submission → Next Study**")
st.markdown("The supporting layers audit evidence, causality, bias, statistics, robustness, reproducibility, generalizability, mechanism, novelty and reviewer risk while project infrastructure preserves artifacts, provenance, permissions, history and reusable knowledge.")

st.info("Important: this page is the integration architecture and command-center milestone. Existing modules still need systematic runtime testing, shared-state wiring, cloud persistence, authentication enforcement and deployment hardening before SciMantra should be treated as a production Research OS.")
st.caption("Module 100 · Architecture complete · Integration and validation phase begins next.")
