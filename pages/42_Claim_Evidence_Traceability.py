import streamlit as st
import pandas as pd
from src.scimantra.claim_traceability import trace_claim, audit_claims

st.set_page_config(page_title="Claim Evidence Traceability | SciMantra", page_icon="🔎", layout="wide")
st.title("🔎 Claim → Evidence Traceability")
st.caption("Audit whether important manuscript claims have an identifiable evidence trail.")

if "claim_records" not in st.session_state:
    st.session_state.claim_records = []

with st.form("claim_form"):
    claim = st.text_area("Manuscript claim", placeholder="Paste one important sentence from your manuscript…")
    evidence = st.text_input("Evidence location", placeholder="Table 2, Figure 3, Methods p. 6, DOI, dataset ID, etc.")
    evidence_type = st.selectbox("Evidence type", ["Dataset", "Statistical analysis", "Figure/Table", "Experimental method", "Literature", "Other", "Not specified"])
    support = st.selectbox("Researcher-assessed support", ["Supported", "Partially supported", "Contradicted", "Not assessed"])
    submitted = st.form_submit_button("Add claim to audit")

if submitted and claim.strip():
    st.session_state.claim_records.append(trace_claim(claim, evidence, evidence_type, support))

if st.session_state.claim_records:
    audit = audit_claims(st.session_state.claim_records)
    c1, c2, c3 = st.columns(3)
    c1.metric("Claims", audit["total"])
    c2.metric("Evidence-linked", audit["linked"])
    c3.metric("Traceability", f"{audit['coverage_percent']}%")
    st.dataframe(pd.DataFrame(st.session_state.claim_records), use_container_width=True, hide_index=True)
    st.download_button("Download traceability CSV", pd.DataFrame(st.session_state.claim_records).to_csv(index=False), "claim_evidence_traceability.csv", "text/csv")
else:
    st.info("Add important Results, Discussion, Introduction, and Conclusion claims one at a time. Empty evidence locations remain explicitly unlinked.")

st.warning("This tool does not decide whether a claim is scientifically true. It detects claim strength and missing traceability so the researcher can verify the underlying source.")
