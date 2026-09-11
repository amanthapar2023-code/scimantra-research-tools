"""Phase 107 — Research OS Decision & Learning Memory."""
import pandas as pd
import streamlit as st
from scimantra.research_os_data_bus import new_bus
from scimantra.research_os_decision_memory import KINDS, OUTCOMES, audit, export_json, record, reusable_lessons, search, summary

st.set_page_config(page_title="SciMantra — Decision Memory", page_icon="🧠", layout="wide")
st.title("🧠 Phase 107 — Research OS Decision & Learning Memory")
st.caption("Keep the reasoning behind research decisions—and the lessons from failed approaches—available across the project.")
st.info("This memory stores researcher-supplied decisions, rationale and outcomes. It does not determine scientific truth or replace primary evidence.")

if "research_os_memory" not in st.session_state: st.session_state.research_os_memory = {"schema_version": 1, "project_id": "", "records": [], "updated_at": ""}
if "research_os_bus" not in st.session_state: st.session_state.research_os_bus = new_bus()
m = summary(st.session_state.research_os_memory)
cols = st.columns(4)
cols[0].metric("Records", m["records"]); cols[1].metric("Decisions", m["decisions"]); cols[2].metric("Failed approaches", m["failed_approaches"]); cols[3].metric("Follow-up", m["follow_up"])

t1,t2,t3,t4 = st.tabs(["Add memory","Search","Reusable lessons","Audit & Export"])
with t1:
    with st.form("memory_form"):
        c1,c2=st.columns(2)
        with c1:
            rid=st.text_input("Memory ID",placeholder="DEC-001")
            kind=st.selectbox("Memory type",KINDS)
            title=st.text_input("Decision / lesson title",placeholder="Use lower exposure range in next experiment")
            outcome=st.selectbox("Outcome",OUTCOMES)
        with c2:
            stage=st.text_input("Research stage",placeholder="04 Experiment")
            rationale=st.text_area("Rationale / what was learned",placeholder="Why was this choice made? What happened?")
            evidence=st.text_input("Evidence artifact IDs (comma-separated)",placeholder="RES-004, DATA-002")
            tags=st.text_input("Tags (comma-separated)",placeholder="dose,optimization")
        save=st.form_submit_button("🧠 Save memory",type="primary")
    if save:
        try:
            st.session_state.research_os_memory=record(st.session_state.research_os_memory,rid,kind,title,rationale,outcome,[x.strip() for x in evidence.split(",")],stage,[x.strip() for x in tags.split(",")]); st.success("Research memory saved."); st.rerun()
        except Exception as exc: st.error(str(exc))
with t2:
    q=st.text_input("Search decisions, lessons, rationale, tags…")
    k=st.selectbox("Filter type",[""]+KINDS)
    rows=search(st.session_state.research_os_memory,q,k)
    st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True) if rows else st.info("No matching memory records.")
with t3:
    lessons=reusable_lessons(st.session_state.research_os_memory)
    st.subheader("Reusable lessons and failed approaches")
    st.caption("These records can inform future experimental planning and next-action review, but remain researcher judgments.")
    st.dataframe(pd.DataFrame(lessons),use_container_width=True,hide_index=True) if lessons else st.info("No reusable lessons recorded yet.")
with t4:
    a=audit(st.session_state.research_os_memory,st.session_state.research_os_bus)
    st.metric("Follow-up records",a["follow_up"])
    if a["duplicates"]: st.error("Duplicate memory IDs: "+", ".join(a["duplicates"]))
    if a["broken_evidence"]: st.warning("Some evidence IDs are not present on the shared bus."); st.dataframe(pd.DataFrame(a["broken_evidence"]),use_container_width=True,hide_index=True)
    elif a["healthy"]: st.success("Memory structure passes audit.")
    st.download_button("⬇️ Export decision memory JSON",export_json(st.session_state.research_os_memory),file_name="scimantra_decision_memory.json",mime="application/json")

st.divider(); st.caption("Phase 107 boundary: research memory and traceability. Memory entries are not automatic scientific conclusions.")
