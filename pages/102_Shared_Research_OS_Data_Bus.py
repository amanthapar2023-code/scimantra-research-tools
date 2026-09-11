import json
import pandas as pd
import streamlit as st
from src.scimantra.research_os_data_bus import new_bus, ensure_bus, register_artifact, link_artifacts, record_event, attach_provenance, audit_bus, snapshot, load_snapshot, summary
from src.scimantra.research_os_state import STAGE_NAMES

st.set_page_config(page_title="Research OS Data Bus", page_icon="🔗", layout="wide")
if "research_os_bus" not in st.session_state: st.session_state.research_os_bus = new_bus()
bus = ensure_bus(st.session_state.research_os_bus)

st.title("🔗 Phase 102 — Shared Research OS Data Bus")
st.caption("One explicit in-session context for project, artifacts, relationships, provenance and audit events.")
st.warning("This is a shared-state prototype. It does not replace production persistence, authentication, or scientific validation.")

s = summary(bus); c = st.columns(6)
c[0].metric("Artifacts", s["artifacts"]); c[1].metric("Links", s["links"]); c[2].metric("Events", s["events"]); c[3].metric("Provenance", s["provenance"]); c[4].metric("Complete stages", s["complete_stages"]); c[5].metric("Blocked", s["blocked_stages"])

st.divider()
t1,t2,t3,t4,t5 = st.tabs(["📦 Artifacts","🔗 Linkage","🧾 Provenance","🕒 Events","💾 Snapshot"])
with t1:
    st.subheader("Register an artifact on the canonical bus")
    with st.form("bus_artifact"):
        a,b = st.columns(2); ident=a.text_input("Artifact ID", "ART-001"); title=b.text_input("Title")
        a,b = st.columns(2); typ=a.text_input("Type", "Dataset"); stage=b.selectbox("Research stage", [""]+STAGE_NAMES)
        a,b = st.columns(2); tool=a.text_input("Source tool"); loc=b.text_input("Location / DOI / URL")
        if st.form_submit_button("Register artifact", type="primary"):
            try:
                bus=register_artifact(bus,ident,title,typ,stage,tool,loc); bus=record_event(bus,"Researcher","Created",ident,typ,"Registered on shared bus"); st.session_state.research_os_bus=bus; st.success("Artifact registered."); st.rerun()
            except ValueError as e: st.error(str(e))
    if bus["artifacts"]: st.dataframe(pd.DataFrame(bus["artifacts"]), use_container_width=True, hide_index=True)
with t2:
    st.subheader("Create explicit artifact relationships")
    ids=[a.get("id") for a in bus["artifacts"]]
    if len(ids)>=2:
        a,b,c=st.columns(3); src=a.selectbox("Source",ids); dst=b.selectbox("Target",ids,index=1); typ=c.selectbox("Relationship",["derived_from","supports","tests","uses","contradicts","revises","cites"])
        note=st.text_input("Relationship note")
        if st.button("Link artifacts",type="primary"):
            try: bus=link_artifacts(bus,src,dst,typ,note); bus=record_event(bus,"Researcher","Linked",dst,"Artifact",f"{src} —{typ}→ {dst}"); st.session_state.research_os_bus=bus; st.success("Relationship added."); st.rerun()
            except ValueError as e: st.error(str(e))
        if bus["links"]: st.dataframe(pd.DataFrame(bus["links"]),use_container_width=True,hide_index=True)
    else: st.info("Register at least two artifacts to create a relationship.")
with t3:
    st.subheader("Attach provenance")
    ids=[a.get("id") for a in bus["artifacts"]]
    if ids:
        a,b=st.columns(2); aid=a.selectbox("Artifact",ids); status=b.selectbox("Status",["Not assessed","Verified","Partially verified","Needs source","Needs verification"])
        a,b=st.columns(2); source=a.text_input("Source / citation"); parent=b.selectbox("Parent artifact",[""]+ids)
        note=st.text_area("Provenance note")
        if st.button("Save provenance",type="primary"):
            try: bus=attach_provenance(bus,aid,source,parent,status,note); bus=record_event(bus,"Researcher","Updated",aid,"Provenance","Attached provenance record"); st.session_state.research_os_bus=bus; st.success("Provenance saved."); st.rerun()
            except ValueError as e: st.error(str(e))
    if bus["provenance"]: st.dataframe(pd.DataFrame(bus["provenance"]),use_container_width=True,hide_index=True)
with t4:
    st.subheader("Record an audit event")
    a,b,c=st.columns(3); actor=a.text_input("Actor","Researcher"); action=b.selectbox("Action",["Created","Updated","Status changed","Linked","Unlinked","Approved","Archived","Exported"]); eid=c.text_input("Entity ID")
    detail=st.text_area("Details")
    if st.button("Record event"):
        bus=record_event(bus,actor,action,eid,"Artifact",detail); st.session_state.research_os_bus=bus; st.success("Event recorded."); st.rerun()
    if bus["events"]: st.dataframe(pd.DataFrame(bus["events"]),use_container_width=True,hide_index=True)
with t5:
    st.subheader("Inspect and transfer the bus")
    audit=audit_bus(bus); st.write({"healthy":audit["healthy"],"duplicate IDs":audit["duplicate_artifact_ids"],"broken links":len(audit["broken_links"]),"broken provenance":len(audit["broken_provenance"])})
    st.download_button("⬇️ Export Research OS bus JSON",snapshot(bus),"scimantra_research_os_bus.json","application/json")
    uploaded=st.file_uploader("Import bus snapshot",type=["json"])
    if uploaded is not None and st.button("Load imported snapshot"):
        try: st.session_state.research_os_bus=load_snapshot(uploaded.getvalue().decode("utf-8")); st.success("Snapshot loaded."); st.rerun()
        except ValueError as e: st.error(str(e))
    st.code(json.dumps(audit,indent=2,default=str),language="json")

st.caption("Phase 102 · Canonical coordination bus · Session-backed prototype")
