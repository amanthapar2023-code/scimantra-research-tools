import pandas as pd
import streamlit as st
from src.scimantra.evidence_sufficiency import EVIDENCE_TYPES, STATUSES, assess_claim, summarize, priority_queue, export_sufficiency

st.set_page_config(page_title="Evidence Sufficiency Engine | SciMantra", page_icon="🧾", layout="wide")
st.title("🧾 Evidence Sufficiency Engine")
st.caption("Ask whether the evidence you have is actually sufficient for the exact claim you want to make.")
st.warning("Integrity rule: this engine audits researcher-supplied evidence and documentation. It does not determine scientific truth or replace expert judgment.")

if "sufficiency_records" not in st.session_state:
    st.session_state.sufficiency_records = []

with st.form("sufficiency_form"):
    claim = st.text_area("Exact manuscript claim", height=130, placeholder="Paste the sentence you intend to publish.")
    evidence = st.text_area("Evidence anchor / observation", height=100, placeholder="Dataset, result, Figure/Table, experimental observation, or verified literature finding")
    evidence_type = st.selectbox("Primary evidence type", EVIDENCE_TYPES)
    support = st.selectbox("Your assessment of support", STATUSES)
    design = st.text_area("Study design / analysis context", height=90, placeholder="Design, experimental unit, comparator, statistical analysis, etc.")
    robustness = st.selectbox("Robustness status", ["Not assessed", "Stable", "Mostly stable", "Sensitive", "Fragile"])
    provenance = st.text_input("Provenance / source location", placeholder="Dataset ID, Figure 2, Table 3, DOI/page, analysis output…")
    add = st.form_submit_button("🧾 Assess evidence sufficiency", type="primary", use_container_width=True)

if add:
    if claim.strip():
        st.session_state.sufficiency_records.append(assess_claim(claim, evidence, evidence_type, support, design, robustness, provenance))
        st.success("Claim added to evidence sufficiency audit.")
    else:
        st.warning("Enter the exact claim first.")

records = st.session_state.sufficiency_records
if records:
    s = summarize(records)
    st.divider()
    st.subheader("1. Evidence sufficiency dashboard")
    a,b,c,d = st.columns(4)
    a.metric("Claims", s["claims"])
    b.metric("Mean score", f"{s['mean_score']}/100")
    c.metric("Supported", s["supported"])
    d.metric("Insufficient / contradictory", s["insufficient"] + s["contradictory"])
    st.dataframe(pd.DataFrame([{**r, "Score": __import__('src.scimantra.evidence_sufficiency', fromlist=['evidence_score']).evidence_score(r)} for r in records]), use_container_width=True, hide_index=True)

    st.subheader("2. Evidence gap priority queue")
    queue = priority_queue(records)
    st.dataframe(pd.DataFrame(queue), use_container_width=True, hide_index=True)

    st.subheader("3. Researcher checkpoint")
    st.info("For each important claim, identify the exact observation that supports it, the analysis that produced it, the study-design feature that makes the inference reasonable, and the provenance location where another researcher can verify it.")
    st.download_button("⬇️ Export evidence sufficiency audit", export_sufficiency(records, s), "scimantra_evidence_sufficiency_audit.md", "text/markdown", use_container_width=True)
else:
    st.info("Add important manuscript claims one at a time. The engine keeps missing evidence visible rather than inventing support.")

st.subheader("What 'sufficient' should mean")
for item in [
    "The evidence directly addresses the claim rather than merely being related to the topic.",
    "The study design and analysis support the type of inference being made.",
    "The evidence has a traceable source or provenance location.",
    "Important contradictions, alternative explanations, and robustness issues have been considered.",
    "The wording is no stronger than the evidence warrants.",
]:
    st.write("• " + item)

st.warning("A high score is a structured planning signal, not a certificate that a claim is true, causal, novel, or publishable.")
