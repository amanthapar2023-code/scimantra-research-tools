"""SciMantra Research OS — Cross-Project Knowledge Engine."""
import pandas as pd
import streamlit as st
from src.scimantra.cross_project_knowledge import KNOWLEDGE_TYPES,new_index,add_record,search,reusable

st.set_page_config(page_title="Cross-Project Knowledge Engine",page_icon="🧠",layout="wide")
st.title("🧠 Cross-Project Knowledge Engine")
st.caption("Turn completed and active projects into reusable research knowledge.")
st.warning("This index is researcher-supplied. Similarity/search does not establish scientific validity, causality, novelty or correctness.")
if "knowledge_index" not in st.session_state: st.session_state.knowledge_index=new_index()
idx=st.session_state.knowledge_index

with st.form("knowledge_record"):
    c=st.columns(3); pid=c[0].text_input("Project ID"); kind=c[1].selectbox("Knowledge type",KNOWLEDGE_TYPES); title=c[2].text_input("Title")
    summary=st.text_area("Finding / method / lesson"); tags=st.text_input("Tags",placeholder="microbiology, wastewater, qPCR")
    if st.form_submit_button("Add to knowledge index",type="primary"):
        add_record(idx,pid,kind,title,summary,tags); st.success("Knowledge record added.")

c1,c2=st.columns(2); q=c1.text_input("Search across projects"); c2.metric("Reusable records",len(reusable(idx)))
results=search(idx,q)
st.subheader("Knowledge search")
if results: st.dataframe(pd.DataFrame(results),use_container_width=True,hide_index=True)
else: st.info("No matching knowledge records yet.")

st.subheader("Reusable research assets")
rr=reusable(idx)
if rr: st.dataframe(pd.DataFrame(rr),use_container_width=True,hide_index=True)
else: st.info("Add methods, findings, gaps, datasets or failed approaches to build the reuse layer.")
st.caption("Module 98 · Cross-project institutional research memory.")
