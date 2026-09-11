import pandas as pd
import streamlit as st

from scimantra.research_os_tool_adapters import TOOL_REGISTRY, audit_adapters, publish_link, publish_output, summary, tool_contracts
from scimantra.research_os_data_bus import audit_bus, new_bus, snapshot

st.set_page_config(page_title="SciMantra — Tool Adapters", page_icon="🔌", layout="wide")
st.title("Phase 103 — Research OS ↔ Tool Adapters")
st.caption("Explicit adapter contracts that let existing SciMantra tools publish outputs into the shared Research OS bus.")

if "research_os_bus" not in st.session_state:
    st.session_state.research_os_bus = new_bus()
bus = st.session_state.research_os_bus

s = summary()
a = audit_bus(bus)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Registered tools", s["registered_tools"])
c2.metric("Bus artifacts", a["artifact_count"])
c3.metric("Bus links", a["link_count"])
c4.metric("Bus events", a["event_count"])

st.divider()
tab1, tab2, tab3, tab4 = st.tabs(["Tool Registry", "Publish Output", "Link Outputs", "Adapter Audit"])

with tab1:
    st.subheader("Existing-tool adapter registry")
    st.dataframe(pd.DataFrame(tool_contracts()), use_container_width=True, hide_index=True)
    st.info("The registry is an explicit routing map. It does not claim that an imported module is scientifically correct or production-ready.")

with tab2:
    st.subheader("Publish a tool output")
    tool = st.selectbox("Source tool", list(TOOL_REGISTRY))
    artifact_id = st.text_input("Artifact ID", placeholder="LIT-001")
    title = st.text_input("Output title", placeholder="Literature evidence set")
    artifact_type = st.selectbox("Artifact type", ["Question", "Literature", "Evidence", "Hypothesis", "Protocol", "Dataset", "Analysis", "Result", "Figure", "Table", "Claim", "Manuscript", "Review", "Other"])
    location = st.text_input("Location / reference", placeholder="Tool output, file path, DOI, or record ID")
    if st.button("Publish to Research OS bus", type="primary"):
        try:
            st.session_state.research_os_bus = publish_output(bus, tool, artifact_id, title, artifact_type, "", location)
            st.success(f"Published {artifact_id} from {tool}.")
        except Exception as exc:
            st.error(str(exc))

with tab3:
    st.subheader("Create an explicit relationship")
    ids = [x.get("id", "") for x in bus.get("artifacts", [])]
    if len(ids) < 2:
        st.warning("Register at least two artifacts first.")
    else:
        source = st.selectbox("Source artifact", ids, key="adapter_source")
        target = st.selectbox("Target artifact", [x for x in ids if x != source], key="adapter_target")
        link_type = st.selectbox("Relationship", ["derived_from", "supports", "tests", "uses", "contradicts", "revises", "cites"])
        note = st.text_input("Link note")
        if st.button("Link artifacts"):
            try:
                st.session_state.research_os_bus = publish_link(bus, source, target, link_type, note)
                st.success("Relationship added to the shared bus.")
            except Exception as exc:
                st.error(str(exc))

with tab4:
    st.subheader("Adapter contract audit")
    if st.button("Run adapter audit", type="primary"):
        st.session_state.adapter_audit = audit_adapters()
    result = st.session_state.get("adapter_audit")
    if result:
        x1, x2, x3 = st.columns(3)
        x1.metric("Passed", result["passed"])
        x2.metric("Failed", result["failed"])
        x3.metric("Coverage", f"{result['coverage_pct']}%")
        st.dataframe(pd.DataFrame(result["rows"]), use_container_width=True, hide_index=True)
    st.subheader("Current bus snapshot")
    st.download_button("Export shared bus JSON", snapshot(bus), file_name="scimantra_research_os_bus.json", mime="application/json")

st.divider()
st.caption("Integrity boundary: adapters move researcher-selected records between tools; they do not infer validity, causality, novelty, authorship, or citation support.")
