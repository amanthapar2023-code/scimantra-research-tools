import streamlit as st
import pandas as pd
from src.scimantra.evidence_extraction import (
    FIELDS, extract_candidates, build_extraction_record, accept_candidate,
    audit_extraction, export_extraction,
)

st.set_page_config(page_title="Evidence Extraction Engine | SciMantra", page_icon="🧩", layout="wide")
st.title("🧩 Evidence Extraction Engine")
st.caption("Turn source text into reviewable evidence candidates for the SciMantra literature matrix — without inventing findings.")

if "extraction_record" not in st.session_state:
    st.session_state.extraction_record = None
if "extraction_candidates" not in st.session_state:
    st.session_state.extraction_candidates = []

with st.form("evidence_extraction"):
    title = st.text_input("Paper title", value=st.session_state.get("ri_title", ""), placeholder="Enter the paper title")
    source = st.text_input("Source anchor", placeholder="DOI, URL, PMID, or citation key")
    location = st.text_input("Known source location (optional)", placeholder="Abstract, Methods §2, p. 5, Table 2…")
    text = st.text_area("Paste abstract or full-text excerpt", height=280, placeholder="Paste text from the paper you have access to. The engine will surface candidate source sentences only.")
    run = st.form_submit_button("🧩 Extract evidence candidates", type="primary")

if run:
    if not title.strip() or not text.strip():
        st.warning("Provide a paper title and source text first.")
    else:
        st.session_state.extraction_record = build_extraction_record(title, text, source, location)
        st.session_state.extraction_candidates = extract_candidates(text)

record = st.session_state.extraction_record
candidates = st.session_state.extraction_candidates

if record is not None:
    st.divider()
    st.subheader("1. Candidate evidence")
    st.caption("These are exact source sentences surfaced by transparent keyword heuristics. They are candidates, not verified interpretations. Review the paper before accepting them.")
    if candidates:
        cdf = pd.DataFrame(candidates)
        st.dataframe(cdf, use_container_width=True, hide_index=True)

        st.subheader("2. Accept a candidate into the matrix")
        selected = st.selectbox("Candidate", range(len(candidates)), format_func=lambda i: f"{candidates[i]['Field']} — {candidates[i]['Candidate excerpt'][:110]}…")
        candidate = candidates[selected]
        field = st.selectbox("Matrix field", FIELDS, index=FIELDS.index(candidate["Field"]))
        accepted_location = st.text_input("Evidence location for accepted excerpt", value=str(candidate["Evidence location"]))
        if st.button("✓ Accept candidate", type="primary"):
            st.session_state.extraction_record = accept_candidate(record, field, str(candidate["Candidate excerpt"]), accepted_location)
            st.success(f"Accepted source excerpt into: {field}")
            record = st.session_state.extraction_record
    else:
        st.info("No candidate sentences were detected. This is not evidence that the paper lacks these elements; review the source manually.")

    st.divider()
    st.subheader("3. Evidence matrix record")
    audit = audit_extraction(record)
    m1, m2, m3 = st.columns(3)
    m1.metric("Evidence coverage", f"{audit['Coverage %']}%")
    m2.metric("Fields populated", f"{audit['Fields populated']}/{audit['Total evidence fields']}")
    m3.metric("Status", audit["Status"])

    editable = {}
    for field in FIELDS:
        editable[field] = st.text_area(field, value=str(record.get(field, "")), key=f"extract_{field}")
    record.update(editable)
    record["Status"] = audit_extraction(record)["Status"]
    st.session_state.extraction_record = record

    st.download_button("Export evidence record (CSV)", pd.DataFrame([record]).to_csv(index=False), "evidence_extraction_record.csv", "text/csv")
    st.download_button("Export evidence record (Markdown)", export_extraction([record]), "evidence_extraction_record.md", "text/markdown")

st.info("Integrity rule: the engine does not generate missing evidence. Empty fields mean evidence still needs to be located and verified in the paper. Candidate excerpts must be checked against the original source before being treated as evidence.")
