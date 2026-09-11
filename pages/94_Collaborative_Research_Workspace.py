"""SciMantra Research OS — Collaborative Research Workspace."""
import pandas as pd
import streamlit as st
from src.scimantra.collaborative_research_workspace import ROLES,TASK_STATUSES,project_summary,priority_tasks

st.set_page_config(page_title="Collaborative Research Workspace",page_icon="👥",layout="wide")
st.title("👥 Collaborative Research Workspace")
st.caption("Coordinate researchers, responsibilities and project tasks around one shared research objective.")
st.warning("This is a project-coordination layer. Access control, simultaneous editing and persistent cloud collaboration will be added in later infrastructure modules.")
if "collab_members" not in st.session_state: st.session_state.collab_members=[]
if "collab_tasks" not in st.session_state: st.session_state.collab_tasks=[]

st.subheader("Research team")
with st.form("member_form"):
    c=st.columns(3); name=c[0].text_input("Researcher name"); role=c[1].selectbox("Role",ROLES); area=c[2].text_input("Area / responsibility")
    if st.form_submit_button("Add team member"): st.session_state.collab_members.append({"name":name,"role":role,"responsibility":area})
if st.session_state.collab_members: st.dataframe(pd.DataFrame(st.session_state.collab_members),use_container_width=True,hide_index=True)

st.divider(); st.subheader("Project task board")
with st.form("task_form"):
    c=st.columns(4); title=c[0].text_input("Task"); owner=c[1].text_input("Owner"); priority=c[2].selectbox("Priority",["High","Medium","Low"]); status=c[3].selectbox("Status",TASK_STATUSES)
    artifact=st.text_input("Related artifact / module"); due=st.text_input("Target date")
    if st.form_submit_button("Add task",type="primary"): st.session_state.collab_tasks.append({"task":title,"owner":owner,"priority":priority,"status":status,"artifact":artifact,"target":due})

r=project_summary(st.session_state.collab_members,st.session_state.collab_tasks)
a,b,c,d,e=st.columns(5); a.metric("Researchers",r["members"]); b.metric("Tasks",r["tasks"]); c.metric("Active",r["active"]); d.metric("Blocked",r["blocked"]); e.metric("Complete",r["complete"])

st.subheader("Priority work")
q=priority_tasks(st.session_state.collab_tasks)
if q: st.dataframe(pd.DataFrame(q),use_container_width=True,hide_index=True)
else: st.info("No open tasks yet.")

st.subheader("Complete task matrix")
if st.session_state.collab_tasks:
    df=pd.DataFrame(st.session_state.collab_tasks); st.dataframe(df,use_container_width=True,hide_index=True)
    st.download_button("Download task matrix CSV",df.to_csv(index=False),"scimantra_collaborative_tasks.csv","text/csv")
else: st.info("Add tasks to build the shared project board.")
st.caption("Module 94 · Collaborative project coordination layer.")
