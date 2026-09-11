"""SciMantra Research OS — transparent next-action planner."""
import pandas as pd
import streamlit as st
from src.scimantra.research_workflow_automation import plan, summary
from src.scimantra.research_os_state import new_project

st.set_page_config(page_title="Research Workflow Automation", page_icon="⚙️", layout="wide")
if "os_project_data" not in st.session_state: st.session_state.os_project_data = new_project()
project = st.session_state.os_project_data
st.title("⚙️ Research Workflow Automation")
st.caption("A transparent planner that tells you what should happen next in the research lifecycle.")
st.info("Recommendations are rule-based decision support. SciMantra does not automatically execute experiments, alter scientific conclusions, or submit manuscripts.")
actions = plan(project); s = summary(actions)
m = st.columns(4)
m[0].metric("Recommended actions", s["total"]); m[1].metric("Critical", s["critical"]); m[2].metric("High", s["high"]); m[3].metric("Medium", s["medium"])
st.divider(); st.subheader("🎯 What should I do next?")
if not actions: st.success("No outstanding workflow actions detected. Review the project manually before beginning the next study cycle.")
else:
    for i,item in enumerate(actions[:12],1):
        with st.container(border=True):
            c1,c2=st.columns([1.8,1])
            with c1:
                badge="🔴" if item["priority"]=="Critical" else "🟠" if item["priority"]=="High" else "🟡"
                st.markdown(f"### {badge} {i}. {item['title']}"); st.write(item["reason"])
            with c2:
                st.metric("Priority",item["priority"]); st.caption(f"Stage: {item['stage']}"); st.caption(f"Suggested tool: **{item['suggested_tool']}**")
st.divider(); st.subheader("📋 Automation queue")
if actions: st.dataframe(pd.DataFrame(actions),use_container_width=True,hide_index=True)
st.subheader("How the planner works")
st.markdown("**1. Reads project stage status** → **2. Checks blocked or unfinished stages** → **3. Prioritizes scientific readiness** → **4. Adds artifact-quality warnings when supplied** → **5. Produces a transparent next-action queue.**")
st.caption("Module 81 · Research Workflow Automation · Transparent rule-based decision support.")
