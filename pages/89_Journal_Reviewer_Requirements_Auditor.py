"""SciMantra Research OS — Journal & Reviewer Requirements Auditor."""
import pandas as pd
import streamlit as st
from src.scimantra.journal_requirements_auditor import REQUIREMENTS, STATUSES, audit, next_actions

st.set_page_config(page_title="Journal Requirements Auditor", page_icon="📋", layout="wide")
st.title("📋 Journal & Reviewer Requirements Auditor")
st.caption("Check manuscript completeness against a configurable journal-style submission checklist.")
st.warning("This is a configurable readiness checklist, not a prediction of editorial acceptance or a substitute for the journal's current author guidelines.")

c1,c2=st.columns(2)
word_count=c1.number_input("Current manuscript word count",min_value=0,value=0,step=100)
word_limit=c2.number_input("Journal word limit (0 = not configured)",min_value=0,value=0,step=100)

statuses={}
st.subheader("Requirements")
for i,(label,key) in enumerate(REQUIREMENTS):
    col1,col2=st.columns([3,2])
    col1.write(label)
    statuses[key]=col2.selectbox(label,STATUSES,key=f"req_{i}",label_visibility="collapsed")

result=audit(statuses,word_count,word_limit)
a,b,c,d=st.columns(4)
a.metric("Present",result["present"]); b.metric("Needs revision",len(result["revision"])); c.metric("Not checked",len(result["missing"])); d.metric("Word limit","OK" if result["word_limit_ok"] else "Exceeded")

if result["ready"]: st.success("Checklist is structurally complete under the configured requirements.")
else: st.error("Submission checklist is not yet ready.")

st.subheader("Priority actions")
for x in next_actions(result): st.write("→",x)

rows=[{"Requirement":label,"Status":statuses.get(key,"Not checked")} for label,key in REQUIREMENTS]
df=pd.DataFrame(rows)
st.subheader("Audit table")
st.dataframe(df,use_container_width=True,hide_index=True)
st.download_button("Download audit CSV",df.to_csv(index=False),"scimantra_journal_requirements_audit.csv","text/csv")
st.caption("Module 89 · Journal/reviewer requirements layer · verify against the target journal before submission.")
