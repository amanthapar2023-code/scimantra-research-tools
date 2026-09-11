"""Phase 109 — Research OS Unified Project Intelligence."""
import pandas as pd
import streamlit as st
from scimantra.research_os_data_bus import new_bus
from scimantra.research_os_unified_intelligence import analyze, summary

st.set_page_config(page_title="SciMantra — Unified Intelligence", page_icon="🧠", layout="wide")
st.title("🧠 Phase 109 — Research OS Unified Project Intelligence")
st.caption("A single decision-support layer connecting context, workflow, artifacts, memory, audits and next actions.")
st.info("This dashboard summarizes explicit project records. The health score is an engineering/readiness signal, not a measure of scientific truth.")

if "research_os_bus" not in st.session_state: st.session_state.research_os_bus = new_bus()
if "research_os_memory" not in st.session_state: st.session_state.research_os_memory = {"records": []}
if "research_os_workflow_run" not in st.session_state: st.session_state.research_os_workflow_run = {}
if "os_project_data" not in st.session_state: st.session_state.os_project_data = st.session_state.research_os_bus.get("project", {})

report = analyze(st.session_state.os_project_data, st.session_state.research_os_bus, st.session_state.research_os_workflow_run, st.session_state.research_os_memory)
s = summary(report)
a,b,c,d,e = st.columns(5)
a.metric("OS health",f"{s['health_score']}/100"); b.metric("Decision state",s["decision_state"]); c.metric("Workflow",f"{s['workflow_completion']}%"); d.metric("Actions",s["actions"]); e.metric("Bus", "Healthy" if s["bus_healthy"] else "Repair")

if s["health_score"] >= 80: st.success("Research OS state is structurally healthy.")
elif s["health_score"] >= 50: st.warning("Research OS state needs attention before advancing confidently.")
else: st.error("Research OS state has significant structural blockers.")

t1,t2,t3,t4 = st.tabs(["Intelligence","Priority Actions","System Health","Context"])
with t1:
    st.subheader("Unified project intelligence")
    st.write("**Decision state:**",s["decision_state"])
    st.write("**Project:**", report["context"].get("project",{}).get("name","Not recorded"))
    st.write("**Research question:**", report["context"].get("project",{}).get("question","Not recorded"))
    st.subheader("Connected layers")
    st.dataframe(pd.DataFrame([{"Layer":"Context","Status":"Active"},{"Layer":"Workflow","Status":f"{s['workflow_completion']}%"},{"Layer":"Artifacts / Bus","Status":"Healthy" if s["bus_healthy"] else "Needs repair"},{"Layer":"Decision Memory","Status":"Healthy" if s["memory_healthy"] else "Needs repair"},{"Layer":"Next Actions","Status":f"{s['actions']} identified"}]),use_container_width=True,hide_index=True)
with t2:
    rows=report["top_actions"]
    if rows: st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
    else: st.info("No priority action currently identified.")
with t3:
    st.subheader("Workflow audit"); st.json(report["workflow"])
    st.subheader("Data bus audit"); st.json(report["bus"])
    st.subheader("Decision memory audit"); st.json(report["memory"])
with t4:
    st.json(report["context"])

st.divider(); st.caption("Phase 109 boundary: unified project intelligence and readiness coordination. It does not replace scientific judgment or primary evidence.")
