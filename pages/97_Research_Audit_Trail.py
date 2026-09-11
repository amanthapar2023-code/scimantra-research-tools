"""SciMantra Research OS — Research Audit Trail."""
import pandas as pd
import streamlit as st
from src.scimantra.research_audit_trail import ACTIONS,event,append,audit,history

st.set_page_config(page_title="Research Audit Trail",page_icon="🧾",layout="wide")
st.title("🧾 Research Audit Trail")
st.caption("Record a traceable history of important changes across the research workflow.")
st.warning("This prototype records events supplied by the researcher. Production-grade tamper resistance, identity verification and immutable cloud storage require the later infrastructure layer.")
if "research_audit_log" not in st.session_state: st.session_state.research_audit_log=[]

with st.form("audit_event"):
    c=st.columns(4); actor=c[0].text_input("Actor"); action=c[1].selectbox("Action",ACTIONS); etype=c[2].text_input("Entity type",placeholder="Dataset / Claim / Manuscript"); eid=c[3].text_input("Entity ID")
    details=st.text_area("What changed / why?")
    if st.form_submit_button("Record event",type="primary"):
        append(st.session_state.research_audit_log,event(actor,action,etype,eid,details)); st.success("Audit event recorded.")

log=st.session_state.research_audit_log
r=audit(log); a,b,c=st.columns(3); a.metric("Events",r["events"]); b.metric("Actors",r["actors"]); c.metric("Entities tracked",r["entities"])

st.subheader("Audit history")
if log:
    df=pd.DataFrame(log); st.dataframe(df,use_container_width=True,hide_index=True)
    st.download_button("Download audit trail CSV",df.to_csv(index=False),"scimantra_research_audit_trail.csv","text/csv")
else: st.info("No audit events recorded yet.")

st.subheader("Entity history")
lookup=st.text_input("Entity ID to trace")
if lookup:
    rows=history(log,lookup)
    if rows: st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
    else: st.info("No history found for this entity ID.")
st.caption("Module 97 · Research workflow history and traceability layer.")
