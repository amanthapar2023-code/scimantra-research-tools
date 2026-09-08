import pandas as pd
import streamlit as st

from scimantra.causal_lab import (
    audit_score,
    causal_claim_levels,
    causal_design_audit,
    confounder_candidates,
    export_causal_audit,
)

st.set_page_config(page_title="Causal Inference & Confounding Lab | SciMantra", layout="wide")

st.title("Causal Inference & Confounding Lab")
st.caption("Stress-test whether your study design can support the strength of claim you want to make.")

st.warning(
    "Integrity rule: this tool does not prove causality, identify true confounders automatically, "
    "or estimate a treatment effect. It creates a researcher-review checklist."
)

plan = st.session_state.get("experiment_plan", {})
def default(key, fallback):
    value = plan.get(key, "")
    return value if isinstance(value, str) and value.strip() else fallback

col1, col2 = st.columns(2)
with col1:
    hypothesis = st.text_area("Causal hypothesis / intended claim", value=default("Hypothesis", "Changing the primary factor changes the primary outcome."), height=110)
    factor = st.text_input("Exposure / intervention", value=default("Primary factor / exposure", ""))
    outcome = st.text_input("Outcome", value=default("Primary outcome", ""))
with col2:
    comparator = st.text_input("Comparator / reference condition", value=default("Comparator", ""))
    design = st.text_input("Study design / allocation", placeholder="e.g., randomized controlled experiment, cohort, case-control, cross-sectional")
    context = st.text_area("Study context / known variables", placeholder="Paste a short description of your system, protocol, or suspected confounders.", height=110)

if st.button("Run causal design audit", type="primary", use_container_width=True):
    rows = causal_design_audit(hypothesis, factor, outcome, comparator, design)
    st.session_state["causal_audit_rows"] = rows
    st.session_state["causal_candidates"] = confounder_candidates(context)

rows = st.session_state.get("causal_audit_rows", [])
candidates = st.session_state.get("causal_candidates", [])

if rows:
    score = audit_score(rows)
    a, b, c = st.columns(3)
    a.metric("Causal-design readiness", f"{score}%")
    b.metric("Checks", len(rows))
    b.metric("Needs review", sum(r["Status"] == "Needs review" for r in rows))
    c.metric("Confounder domains", len(candidates))

    st.subheader("Causal-design audit")
    st.caption("A check is not considered addressed until the researcher records an actual design decision or evidence plan.")
    for i, row in enumerate(rows):
        with st.expander(f"{i + 1}. {row['Check']} — {row['Status']}"):
            st.write(row["Question"])
            st.caption("Recommended action")
            st.write(row["Recommended evidence / design action"])
            row["Status"] = st.selectbox("Researcher status", ["Needs review", "Addressed"], index=0 if row["Status"] == "Needs review" else 1, key=f"causal_status_{i}")
            row["Researcher notes"] = st.text_area("Researcher notes / protocol decision", row.get("Researcher notes", ""), key=f"causal_notes_{i}")

    st.subheader("Confounder domains to investigate")
    if candidates:
        for item in candidates:
            st.checkbox(item, key=f"confounder_{item}")
    else:
        st.info("Add study context and rerun the audit to generate generic confounder domains.")

    st.subheader("Choose the strongest claim your design can defend")
    st.dataframe(pd.DataFrame(causal_claim_levels()), use_container_width=True, hide_index=True)
    claim_level = st.selectbox("Researcher-selected claim level", [x["Level"] for x in causal_claim_levels()])
    st.info(f"Selected level: {claim_level}. Final claim wording must still be justified by the actual study, data, assumptions, and field-specific standards.")

    export = export_causal_audit(rows, candidates) + f"\n## Researcher-selected claim level\n{claim_level}\n"
    st.download_button("Download causal audit (Markdown)", export, "scimantra_causal_audit.md", "text/markdown", use_container_width=True)
else:
    st.info("Enter your intended causal claim and study design, then run the audit.")
