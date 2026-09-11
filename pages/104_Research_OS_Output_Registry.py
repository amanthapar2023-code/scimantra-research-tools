"""Phase 104 — Research OS Output Registry."""
import pandas as pd
import streamlit as st

from scimantra.research_os_data_bus import audit_bus, new_bus, snapshot
from scimantra.research_os_output_registry import OUTPUT_TYPES, output_record, register_output, registry_audit, summary
from scimantra.research_os_tool_adapters import TOOL_REGISTRY

st.set_page_config(page_title="SciMantra — Output Registry", page_icon="📦", layout="wide")
st.title("📦 Phase 104 — Research OS Output Registry")
st.caption("Standardize specialist-tool outputs before they enter the shared Research OS data bus.")
st.info("This registry checks structure and provenance metadata only. It does not certify scientific correctness or evidence support.")

if "research_os_bus" not in st.session_state:
    st.session_state.research_os_bus = new_bus()
if "os_output_records" not in st.session_state:
    st.session_state.os_output_records = []

records = st.session_state.os_output_records
bus = st.session_state.research_os_bus
s = summary(records)
a = audit_bus(bus)
m = st.columns(5)
m[0].metric("Outputs", s["outputs"]); m[1].metric("Ready", s["ready"]); m[2].metric("Needs review", s["needs_review"]); m[3].metric("Duplicates", s["duplicates"]); m[4].metric("Bus artifacts", a["artifact_count"])

st.divider()
tab1, tab2, tab3, tab4 = st.tabs(["Register Output", "Batch Registry", "Audit", "Bus Snapshot"])

with tab1:
    st.subheader("Register a specialist-tool output")
    tool = st.selectbox("Source tool", list(TOOL_REGISTRY))
    stage = TOOL_REGISTRY[tool][1]
    c1, c2 = st.columns(2)
    with c1:
        artifact_id = st.text_input("Output / artifact ID", placeholder="LIT-001")
        title = st.text_input("Output title", placeholder="Evidence set from literature review")
        artifact_type = st.selectbox("Output type", OUTPUT_TYPES)
    with c2:
        location = st.text_input("Location / reference", placeholder="DOI, file path, tool record, etc.")
        description = st.text_area("Description", placeholder="What did this tool produce?")
        metadata_text = st.text_area("Optional metadata (key=value per line)", placeholder="topic=BTEX\nversion=1")
    st.caption(f"Lifecycle stage assigned by adapter contract: **{stage}**")
    if st.button("➕ Register output", type="primary"):
        metadata = {}
        for line in metadata_text.splitlines():
            if "=" in line:
                k, v = line.split("=", 1); metadata[k.strip()] = v.strip()
        record = output_record(artifact_id, title, artifact_type, tool, stage, location, description, metadata)
        issues = registry_audit(records + [record])
        if any(row["id"] == record["id"] and not row["ready"] for row in issues["rows"]):
            st.error("Output is structurally incomplete. Fix the highlighted fields and try again.")
        elif record["id"] in [r.get("id") for r in records]:
            st.error("That output ID already exists. Use a unique ID.")
        else:
            try:
                st.session_state.research_os_bus = register_output(bus, record)
                records.append(record)
                st.success(f"Registered {record['id']} → {record['source_tool']}")
            except Exception as exc:
                st.error(str(exc))

with tab2:
    st.subheader("Registered outputs")
    if records:
        st.dataframe(pd.DataFrame(records), use_container_width=True, hide_index=True)
    else:
        st.info("No outputs registered yet.")
    st.caption("Outputs remain researcher-selected records; the registry never silently invents results.")

with tab3:
    st.subheader("Registry audit")
    report = registry_audit(records)
    if report["duplicates"]:
        st.error("Duplicate IDs: " + ", ".join(report["duplicates"]))
    if report["rows"]:
        st.dataframe(pd.DataFrame(report["rows"]), use_container_width=True, hide_index=True)
    else:
        st.info("Nothing to audit yet.")
    if report["healthy"]:
        st.success("All registered outputs pass structural checks.")
    else:
        st.warning("Resolve structural issues before treating the registry as ready.")

with tab4:
    st.subheader("Shared Research OS bus")
    bus_audit = audit_bus(st.session_state.research_os_bus)
    st.json(bus_audit)
    st.download_button("Export Research OS bus JSON", snapshot(st.session_state.research_os_bus), file_name="scimantra_research_os_bus.json", mime="application/json")

st.divider()
st.caption("Phase 104 boundary: registration and routing only. Scientific interpretation remains with the researcher.")
