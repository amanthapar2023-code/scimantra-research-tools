import streamlit as st
import pandas as pd
from src.scimantra.citation_integrity import audit_claim, audit_manuscript_claims, export_audit

st.set_page_config(page_title="Citation & Source Integrity | SciMantra", page_icon="🔗", layout="wide")
st.title("🔗 Citation & Source Integrity")
st.caption("Audit manuscript claims for traceability, missing sources, missing evidence and potentially over-strong causal wording.")

if "citation_audit_rows" not in st.session_state:
    st.session_state.citation_audit_rows = []

with st.form("claim_audit"):
    claim = st.text_area("Manuscript claim", height=110, placeholder="Paste one factual or interpretive statement at a time.")
    source = st.text_input("Citation / source anchor", placeholder="DOI, PMID, reference key, URL, section/page, etc.")
    evidence = st.text_area("Evidence location or data support", height=90, placeholder="Page/section/table/figure, dataset column, analysis output, or researcher verification note")
    add = st.form_submit_button("Audit claim", type="primary")

if add:
    if claim.strip():
        st.session_state.citation_audit_rows.append(audit_claim(claim, source, evidence))
        st.success("Claim audited.")
    else:
        st.warning("Enter a claim first.")

rows = st.session_state.citation_audit_rows
if rows:
    metrics = audit_manuscript_claims(rows)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Claims", metrics["total"])
    c2.metric("Fully linked", metrics["fully_linked"])
    c3.metric("Traceability", f"{metrics['coverage']:.1f}%")
    c4.metric("Causal flags", metrics["causal_flags"])
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    st.download_button("Export integrity audit", export_audit(rows), "citation_source_integrity.md", "text/markdown")
else:
    st.info("Add manuscript claims to begin the source-integrity audit.")

st.warning("A detected citation is not proof that the citation supports the claim. Always verify the source itself. This tool does not assess truth, source quality, plagiarism, or journal acceptance.")
