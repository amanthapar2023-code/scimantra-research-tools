"""Phase 108 — Research OS Context Engine."""
import pandas as pd
import streamlit as st
from scimantra.research_os_data_bus import new_bus
from scimantra.research_os_context import build_context, context_summary

st.set_page_config(page_title="SciMantra — Context Engine", page_icon="🧭", layout="wide")
st.title("🧭 Phase 108 — Research OS Context Engine")
st.caption("One contextual view of the project's question, workflow, artifacts, memory and next actions.")
st.info("Context is assembled from explicit researcher/project records. It summarizes state; it does not infer scientific truth, causality or novelty.")

if "research_os_bus" not in st.session_state: st.session_state.research_os_bus = new_bus()
if "research_os_memory" not in st.session_state: st.session_state.research_os_memory = {"records": []}
if "research_os_workflow_run" not in st.session_state: st.session_state.research_os_workflow_run = {}
if "os_project_data" not in st.session_state: st.session_state.os_project_data = st.session_state.research_os_bus.get("project", {})

ctx = build_context(st.session_state.os_project_data, st.session_state.research_os_bus, st.session_state.research_os_workflow_run, st.session_state.research_os_memory)
s = context_summary(ctx)
a,b,c,d,e = st.columns(5)
a.metric("Artifacts",s["artifacts"]); b.metric("Memory",s["memory_records"]); c.metric("Next actions",s["next_actions"]); d.metric("Context flags",s["flags"]); e.metric("Workflow",s["workflow"] or "Not started")

if ctx["context_flags"]:
    st.warning(" · ".join(ctx["context_flags"]))
else: st.success("No contextual gaps detected from the available project records.")

t1,t2,t3,t4 = st.tabs(["Context","Next Actions","Workflow","Export"])
with t1:
    st.subheader("Current research context")
    st.write("**Project:**", s["project"] or "Not recorded")
    project = ctx.get("project",{})
    st.write("**Research question:**", project.get("question", "Not recorded") if isinstance(project,dict) else "Not recorded")
    st.subheader("Shared state")
    st.json({"bus":ctx["bus"],"memory":ctx["memory"]})
with t2:
    st.subheader("Prioritized next actions")
    rows=ctx["next_actions"]
    if rows: st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
    else: st.info("No workflow actions are currently available. Start a workflow in Phase 105.")
with t3:
    st.subheader("Workflow context")
    steps=ctx.get("workflow",{}).get("steps",[])
    if steps: st.dataframe(pd.DataFrame(steps),use_container_width=True,hide_index=True)
    else: st.info("No active workflow run.")
with t4:
    st.subheader("Context snapshot")
    st.download_button("⬇️ Export context JSON",__import__('json').dumps(ctx,indent=2,ensure_ascii=False),file_name="scimantra_research_os_context.json",mime="application/json")
    st.json(ctx)

st.divider(); st.caption("Phase 108 boundary: contextual coordination layer. Scientific decisions remain with the researcher and primary evidence.")
