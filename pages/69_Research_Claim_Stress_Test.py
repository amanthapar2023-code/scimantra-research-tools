import pandas as pd
import streamlit as st
from src.scimantra.claim_stress_test import audit_claim, stress_test, summary, export_stress_test

st.set_page_config(page_title="Research Claim Stress-Test | SciMantra", page_icon="🧨", layout="wide")
st.title("🧨 Research Claim Stress-Test / Overclaim Detector")
st.caption("Try to break the exact wording of a manuscript claim before a reviewer does.")
st.warning("Integrity rule: these are transparent wording heuristics. A flag does not prove a claim is false, and a clean result does not prove it is scientifically valid.")

if "claim_stress_rows" not in st.session_state:
    st.session_state.claim_stress_rows = []

with st.form("claim_stress_form"):
    claim = st.text_area("Exact manuscript claim", height=140, placeholder="Paste one sentence from the Introduction, Results, Discussion, or Conclusion.")
    evidence = st.text_area("Evidence / provenance anchor", height=90, placeholder="Dataset, analysis output, Figure/Table, protocol, DOI/page, or other verified source location")
    design = st.text_area("Study design / analysis context", height=90, placeholder="e.g., randomized controlled experiment, observational cohort, in-vitro study, regression model…")
    source = st.text_input("Literature/source anchor (optional)", placeholder="DOI, citation key, paper section/page…")
    run = st.form_submit_button("🧨 Stress-test this claim", type="primary", use_container_width=True)

if run:
    if not claim.strip():
        st.warning("Enter the exact claim first.")
    else:
        result = audit_claim(claim, evidence, design, source)
        st.session_state.claim_stress_last = result
        st.session_state.claim_stress_rows.append({"ID": f"C{len(st.session_state.claim_stress_rows)+1}", "Claim": claim.strip(), "Evidence": evidence.strip(), "Design": design.strip(), "Source": source.strip()})

last = st.session_state.get("claim_stress_last")
if last:
    st.divider()
    st.subheader("1. Stress-test result")
    st.metric("Claim risk flag", last["Risk level"])
    if last["Flags"]:
        st.dataframe(pd.DataFrame(last["Flags"]), use_container_width=True, hide_index=True)
    else:
        st.success("No heuristic overclaim trigger was detected. Continue with domain-specific verification.")

    st.subheader("2. Evidence alignment checkpoint")
    c1, c2, c3 = st.columns(3)
    c1.metric("Evidence anchor", "Supplied" if last["Evidence supplied"] else "MISSING")
    c2.metric("Design context", "Supplied" if last["Design supplied"] else "MISSING")
    c3.metric("Source anchor", "Supplied" if last["Source supplied"] else "MISSING")
    st.info("Ask: If a skeptical reviewer challenged this exact sentence, can you point to the specific observation, analysis, study-design feature, and source that justify every important word?")

rows = st.session_state.claim_stress_rows
if rows:
    st.divider()
    st.subheader("3. Claim review queue")
    tested = stress_test(rows)
    s = summary(tested)
    a,b,c,d = st.columns(4)
    a.metric("Claims", s["claims"]); b.metric("High", s["high"]); c.metric("Moderate", s["moderate"]); d.metric("Needs review", s["claims_needing_review"])
    st.dataframe(pd.DataFrame(tested), use_container_width=True, hide_index=True)
    st.download_button("⬇️ Export claim stress-test", export_stress_test(tested), "scimantra_claim_stress_test.md", "text/markdown", use_container_width=True)

st.subheader("4. Reviewer questions")
for q in [
    "Does the verb imply causality that the design cannot establish?",
    "Does the sentence claim a mechanism that was not directly measured or tested?",
    "Is statistical evidence being converted into certainty or proof?",
    "Does the claim extend beyond the studied population, system, conditions, or time period?",
    "If novelty is claimed, what is the closest prior work and exactly what differs?",
    "Does every quantitative value match the authoritative result, unit, denominator, and timepoint?",
    "Is the conclusion stronger than the primary endpoint and uncertainty justify?",
]:
    st.write("• " + q)

st.info("Recommended workflow: Claim Stress-Test → Claim/Evidence Traceability → Causal/Confounding Audit → Statistical Assumption Audit → Robustness/Sensitivity → Research Integrity check.")
