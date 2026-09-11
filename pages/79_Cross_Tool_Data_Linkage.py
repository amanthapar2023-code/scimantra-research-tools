"""Cross-Tool Data Linkage — Research OS artifact graph."""
import pandas as pd
import streamlit as st
from src.scimantra.cross_tool_linkage import LINK_TYPES, ensure_bus, register_artifact, link_artifacts, trace, audit_bus

st.set_page_config(page_title="Cross-Tool Data Linkage | SciMantra", page_icon="🔗", layout="wide")
st.title("🔗 Cross-Tool Data Linkage")
st.caption("Connect outputs from specialist SciMantra tools into one explicit research evidence graph.")
st.warning("Integrity rule: links record researcher-defined relationships. They do not prove that an artifact is correct, causal, novel, or publication-ready.")

if "os_link_bus" not in st.session_state:
    st.session_state.os_link_bus = ensure_bus()
bus = st.session_state.os_link_bus

st.subheader("1. Register tool outputs")
with st.form("register"):
    c1,c2 = st.columns(2)
    aid = c1.text_input("Artifact ID", placeholder="e.g., gap-001")
    title = c2.text_input("Artifact title", placeholder="e.g., Verified research gap")
    c3,c4,c5 = st.columns(3)
    atype = c3.selectbox("Type", ["Question","Gap","Hypothesis","Literature","Experiment","Dataset","Analysis","Result","Figure","Table","Claim","Protocol","Manuscript","Review","Other"])
    stage = c4.selectbox("Research stage", ["Research Question","Literature","Hypothesis","Experiment","Data","Analysis","Evidence","Claims","Manuscript","Peer Review","Submission","Next Study"])
    tool = c5.text_input("Producing tool", placeholder="e.g., Research Gap Generator")
    payload = st.text_area("Optional output summary", placeholder="Short researcher-entered summary; avoid sensitive data.")
    if st.form_submit_button("➕ Register artifact", type="primary"):
        try:
            bus = register_artifact(bus, aid, title, atype, stage, tool, payload)
            st.session_state.os_link_bus = bus
            st.success(f"Registered **{title.strip()}**.")
        except ValueError as exc: st.error(str(exc))

st.divider(); st.subheader("2. Link two outputs")
ids = [a.get("id") for a in bus["artifacts"]]
if len(ids) >= 2:
    with st.form("link"):
        c1,c2,c3 = st.columns(3)
        source = c1.selectbox("Source artifact", ids)
        target = c2.selectbox("Target artifact", [x for x in ids if x != source])
        ltype = c3.selectbox("Relationship", LINK_TYPES)
        note = st.text_input("Relationship note", placeholder="Why did you connect these?")
        if st.form_submit_button("🔗 Create link"):
            try:
                bus = link_artifacts(bus, source, target, ltype, note)
                st.session_state.os_link_bus = bus
                st.success("Link added to the research graph.")
            except ValueError as exc: st.error(str(exc))
else:
    st.info("Register at least two artifacts to create an explicit relationship.")

st.divider(); st.subheader("3. Research graph")
if bus["artifacts"]:
    st.dataframe(pd.DataFrame(bus["artifacts"])[["id","title","type","stage","tool","updated_at"]], use_container_width=True, hide_index=True)
if bus["links"]:
    st.dataframe(pd.DataFrame(bus["links"]), use_container_width=True, hide_index=True)

st.subheader("4. Trace an artifact")
if ids:
    selected = st.selectbox("Artifact to trace", ids)
    direction = st.radio("Direction", ["upstream","downstream"], horizontal=True)
    rows = trace(bus, selected, direction=direction)
    if rows: st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else: st.info("No linked artifacts found in that direction.")

st.subheader("5. Linkage audit")
audit = audit_bus(bus)
c1,c2,c3 = st.columns(3); c1.metric("Artifacts", audit["artifacts"]); c2.metric("Links", audit["links"]); c3.metric("Isolated", len(audit["isolated_artifacts"]))
if audit["duplicate_ids"]: st.error("Duplicate artifact IDs: " + ", ".join(audit["duplicate_ids"]))
if audit["broken_links"]: st.error(f"Broken links detected: {len(audit['broken_links'])}")
if not audit["duplicate_ids"] and not audit["broken_links"]: st.success("Graph structure is internally consistent.")

st.download_button("⬇️ Export linkage graph JSON", pd.Series(bus).to_json(indent=2), "scimantra_cross_tool_linkage.json", "application/json", use_container_width=True)
