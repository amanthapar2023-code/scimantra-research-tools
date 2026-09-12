"""Phase 112 — Research OS Data Contract inspector."""
import json
import pandas as pd
import streamlit as st
from scimantra.research_os_data_contract import SCHEMA_VERSION, STATUSES, audit, envelope, export_contract

st.set_page_config(page_title="SciMantra — Data Contract", page_icon="📐", layout="wide")
st.title("📐 Phase 112 — Research OS Data Contract")
st.caption("Canonical exchange envelope for project, artifact, workflow and audit integrations.")
st.info("This contract standardizes structure and interoperability. It does not certify scientific correctness or validate external services.")

if "research_os_contract_records" not in st.session_state: st.session_state.research_os_contract_records=[]
with st.form("contract_record"):
    a,b,c=st.columns(3)
    pid=a.text_input("Project ID", "PROJECT-001"); aid=b.text_input("Artifact ID", placeholder="RES-001"); typ=c.text_input("Artifact type", "Result")
    d,e,f=st.columns(3)
    stage=d.text_input("Lifecycle stage", "06 Analysis"); tool=e.text_input("Source tool", "Results Interpreter"); status=f.selectbox("Status",STATUSES)
    payload=st.text_area("Payload JSON", "{}")
    add=st.form_submit_button("➕ Validate & register contract record",type="primary")
if add:
    try:
        obj=json.loads(payload)
        r=envelope(pid,aid,typ,stage,tool,status,obj); st.session_state.research_os_contract_records.append(r); st.success("Contract record registered.")
    except Exception as exc: st.error(str(exc))

records=st.session_state.research_os_contract_records
audit_result=audit(records)
x,y,z=st.columns(3); x.metric("Records",len(records)); y.metric("Duplicates",len(audit_result["duplicates"])); z.metric("Invalid",len(audit_result["invalid"]))
if audit_result["valid"]: st.success(f"All records satisfy Research OS schema v{SCHEMA_VERSION}.")
else: st.warning("Contract audit found structural issues.")
if records: st.dataframe(pd.DataFrame(records)[["project_id","artifact_id","artifact_type","stage","source_tool","status","schema_version"]],use_container_width=True,hide_index=True)
if audit_result["invalid"]: st.dataframe(pd.DataFrame(audit_result["invalid"]),use_container_width=True,hide_index=True)
st.download_button("⬇️ Export contract package",export_contract(records),file_name="scimantra_research_os_contract.json",mime="application/json")
st.divider(); st.caption("Production target: all integrated tools should emit or adapt to this canonical envelope before cloud persistence and multi-user synchronization.")
