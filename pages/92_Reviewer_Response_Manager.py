"""SciMantra Research OS — Reviewer Response Manager."""
import pandas as pd
import streamlit as st
from src.scimantra.reviewer_response_manager import SEVERITIES, STATUSES, response_template, audit, priority_queue

st.set_page_config(page_title="Reviewer Response Manager",page_icon="🔄",layout="wide")
st.title("🔄 Reviewer Response Manager")
st.caption("Track reviewer comments from receipt through evidence-backed response and resolution.")
st.warning("This manages the revision workflow. It does not determine whether a reviewer is scientifically correct or predict editorial decisions.")
if "review_items" not in st.session_state: st.session_state.review_items=[]

with st.form("review_form"):
    c=st.columns(4)
    rid=c[0].text_input("Comment ID",placeholder="R1-C01")
    reviewer=c[1].text_input("Reviewer",placeholder="Reviewer 1")
    round_no=c[2].text_input("Round",value="1")
    severity=c[3].selectbox("Severity",SEVERITIES)
    comment=st.text_area("Reviewer comment")
    location=st.text_input("Manuscript location",placeholder="Results, paragraph 3")
    response=st.text_area("Author response")
    revision=st.text_area("Revision made")
    evidence=st.text_input("Evidence / analysis anchor")
    status=st.selectbox("Status",STATUSES)
    submit=st.form_submit_button("Add reviewer comment",type="primary")
if submit:
    item=response_template(comment); item.update({"id":rid,"reviewer":reviewer,"round":round_no,"severity":severity,"location":location,"response":response,"revision":revision,"evidence":evidence,"status":status})
    st.session_state.review_items.append(item); st.success("Reviewer comment added.")

items=st.session_state.review_items
r=audit(items)
a,b,c,d=st.columns(4); a.metric("Comments",r["total"]); b.metric("Open",r["open"]); c.metric("Major open",r["major_open"]); d.metric("Resolved",r["resolved"])
if r["ready"]: st.success("No major or required-experiment comments remain open.")
else: st.error("Revision work remains before the response set is ready.")

st.subheader("Priority queue")
queue=priority_queue(items)
if queue: st.dataframe(pd.DataFrame(queue),use_container_width=True,hide_index=True)
else: st.info("No open reviewer comments.")

st.subheader("Revision matrix")
if items:
    df=pd.DataFrame(items); st.dataframe(df[["id","reviewer","round","severity","comment","location","response","revision","evidence","status"]],use_container_width=True,hide_index=True)
    st.download_button("Download response matrix CSV",df.to_csv(index=False),"scimantra_reviewer_response_matrix.csv","text/csv")
else: st.info("Add reviewer comments to build the revision matrix.")
st.caption("Module 92 · Reviewer comment → response → revision → evidence → resolution.")
