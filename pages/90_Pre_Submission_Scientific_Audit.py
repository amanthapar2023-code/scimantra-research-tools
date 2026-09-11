"""SciMantra Research OS — Pre-Submission Scientific Audit."""
import pandas as pd
import streamlit as st
from src.scimantra.pre_submission_scientific_audit import SIGNALS, LEVELS, audit, actions

st.set_page_config(page_title="Pre-Submission Scientific Audit", page_icon="🛡️", layout="wide")
st.title("🛡️ Pre-Submission Scientific Audit")
st.caption("One final scientific-readiness checkpoint before moving a project toward submission.")
st.warning("This is a decision-support audit. It does not predict acceptance, prove scientific validity, or replace expert review.")

signals={}
for i,signal in enumerate(SIGNALS):
    c1,c2=st.columns([3,2]); c1.write(f"**{signal}**"); signals[signal]=c2.selectbox(signal,LEVELS,key=f"audit_{i}",label_visibility="collapsed")

result=audit(signals)
a,b,c,d=st.columns(4)
a.metric("Readiness score",f'{result["score"]}/100'); b.metric("Assessed",f'{result["assessed"]}/{len(SIGNALS)}'); c.metric("Critical gaps",len(result["critical"])); d.metric("Needs work",len(result["needs_work"]))

if result["ready"]: st.success("No critical or needs-work signals remain among the assessed checks.")
else: st.error("Scientific audit is not yet submission-ready.")

st.subheader("Priority actions")
for item in actions(result): st.write("→",item)

rows=[{"Audit signal":k,"Status":v} for k,v in signals.items()]
df=pd.DataFrame(rows)
st.subheader("Scientific readiness matrix")
st.dataframe(df,use_container_width=True,hide_index=True)
st.download_button("Download scientific audit CSV",df.to_csv(index=False),"scimantra_pre_submission_scientific_audit.csv","text/csv")
st.caption("Module 90 · Integrated scientific readiness checkpoint.")
