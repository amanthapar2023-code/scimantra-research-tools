"""SciMantra Research OS — Experiment → Data Integration."""
import pandas as pd
import streamlit as st
from src.scimantra.experiment_data_bridge import FIELDS, new_record, validate, link

st.set_page_config(page_title="Experiment → Data Integration", page_icon="🧪", layout="wide")
st.title("🧪 Experiment → Data Integration")
st.caption("Create a traceable bridge from experimental design to the dataset it produces.")
st.info("This module records relationships and performs structural checks. It does not validate experimental truth or data quality beyond the listed fields.")

if "experiment_records" not in st.session_state: st.session_state.experiment_records=[]
if "experiment_dataset_links" not in st.session_state: st.session_state.experiment_dataset_links=[]

st.subheader("1. Define the experiment → dataset relationship")
a,b,c=st.columns(3)
exp_id=a.text_input("Experiment ID",placeholder="EXP-001"); exp_title=b.text_input("Experiment title"); protocol=c.text_input("Protocol ID",placeholder="PROT-001")
d,e,f=st.columns(3)
data_id=d.text_input("Dataset ID",placeholder="DATA-001"); data_title=e.text_input("Dataset title"); condition=f.text_input("Condition / group")
if st.button("🔗 Register experiment → dataset",type="primary"):
    if not exp_id.strip() or not data_id.strip() or not condition.strip(): st.error("Experiment ID, Dataset ID and Condition are required.")
    else:
        st.session_state.experiment_dataset_links.append(link({'id':exp_id,'title':exp_title},{'id':data_id,'title':data_title})); st.success("Relationship registered.")

st.divider(); st.subheader("2. Register observations / records")
with st.form("record_form"):
    cols=st.columns(5)
    rid=cols[0].text_input("Record ID"); cond=cols[1].text_input("Condition"); n=cols[2].text_input("Sample count"); meas=cols[3].text_input("Measurement"); unit=cols[4].text_input("Unit")
    rep=st.text_input("Replicate"); notes=st.text_area("Notes"); add=st.form_submit_button("Add record")
if add:
    st.session_state.experiment_records.append({"id":rid,"experiment_id":exp_id,"dataset_id":data_id,"protocol_id":protocol,"condition":cond,"sample_count":n,"measurement":meas,"unit":unit,"replicate":rep,"notes":notes})

records=st.session_state.experiment_records
if records: st.dataframe(pd.DataFrame(records)[FIELDS],use_container_width=True,hide_index=True)
else: st.info("No records registered yet.")

st.divider(); st.subheader("3. Structural readiness")
check=validate(records); x,y,z=st.columns(3); x.metric("Records",check["records"]); y.metric("Missing required",len(check["missing_required"])); z.metric("Duplicate IDs",len(check["duplicate_ids"]))
if check["ready"]: st.success("Dataset bridge is structurally ready for the registered records.")
else:
    if check["missing_required"]: st.warning(str(check["missing_required"]))
    if check["duplicate_ids"]: st.error("Duplicate record IDs: "+', '.join(check["duplicate_ids"]))

st.subheader("Registered links")
if st.session_state.experiment_dataset_links: st.dataframe(pd.DataFrame(st.session_state.experiment_dataset_links),use_container_width=True,hide_index=True)

st.caption("Module 85 · Experiment → Data Integration · Structural traceability only.")
