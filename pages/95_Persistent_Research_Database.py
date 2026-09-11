"""SciMantra Research OS — Persistent Research Database."""
import json
import pandas as pd
import streamlit as st
from src.scimantra.persistent_research_store import ENTITY_TYPES,new_store,add_entity,audit_store

st.set_page_config(page_title="Persistent Research Database",page_icon="☁️",layout="wide")
st.title("☁️ Persistent Research Database")
st.caption("Database-ready project store for the SciMantra Research OS.")
st.warning("This module establishes the persistent data model and local session-backed prototype. It does not yet connect to a production cloud database or provide multi-user synchronization.")

if "research_store" not in st.session_state: st.session_state.research_store=new_store()
store=st.session_state.research_store

c1,c2=st.columns(2); store["project_id"]=c1.text_input("Project ID",value=store.get("project_id","PROJECT-001")); c2.metric("Entities",audit_store(store)["total_entities"])

st.subheader("Add research entity")
with st.form("entity_form"):
    c=st.columns(3); kind=c[0].selectbox("Entity type",ENTITY_TYPES); eid=c[1].text_input("Entity ID (optional)"); title=c[2].text_input("Title / name")
    description=st.text_area("Description / metadata")
    if st.form_submit_button("Save entity",type="primary"):
        add_entity(store,kind,{"id":eid.strip() or None,"title":title,"description":description}); st.success("Entity stored in the project database model.")

summary=audit_store(store)
st.subheader("Database inventory")
df=pd.DataFrame([{"Entity type":k,"Count":v} for k,v in summary["entity_counts"].items()])
st.dataframe(df,use_container_width=True,hide_index=True)

st.subheader("Project store")
for kind,records in store["entities"].items():
    if records:
        st.write(f"**{kind.title()}**")
        st.dataframe(pd.DataFrame(records),use_container_width=True,hide_index=True)

st.download_button("Export project store JSON",json.dumps(store,indent=2),"scimantra_research_store.json","application/json")
st.caption("Module 95 · Persistent research data architecture · cloud persistence comes in the production integration phase.")
