import streamlit as st
import pandas as pd
from src.scimantra.experiment_architect import architect, audit_architecture, architecture_score, reviewer_challenges, export_architecture

st.set_page_config(page_title="Research Experiment Architect | SciMantra", page_icon="🧪", layout="wide")
st.title("🧪 Research Experiment Architect")
st.caption("Convert a research question and hypothesis into an editable, auditable experimental blueprint.")

question = st.text_area("Selected research question", placeholder="What exactly will this study test?")
hypothesis = st.text_area("Selected hypothesis", placeholder="State the hypothesis and its potential falsifier.")
c1, c2, c3 = st.columns(3)
factor = c1.text_input("Primary factor / exposure", placeholder="Treatment, concentration, condition…")
outcome = c2.text_input("Primary outcome", placeholder="Measured endpoint + unit")
comparator = c3.text_input("Comparator", placeholder="Control / reference condition")

if st.button("🏗️ Build experiment architecture", type="primary"):
    st.session_state.experiment_plan = architect(question, hypothesis, factor, outcome, comparator)

plan = st.session_state.get("experiment_plan")
if plan:
    st.divider()
    st.subheader("1. Study architecture")
    editable = {}
    for key, value in plan.items():
        if key in {"Research question", "Hypothesis", "Primary factor / exposure", "Primary outcome", "Comparator"}:
            editable[key] = st.text_area(key, value=str(value), key=f"exp_{key}")
        else:
            editable[key] = st.text_area(key, value=str(value), height=90, key=f"exp_{key}")
    plan.update(editable)
    st.session_state.experiment_plan = plan

    audit = audit_architecture(plan)
    score = architecture_score(audit)
    st.subheader("2. Design audit")
    a, b = st.columns(2)
    a.metric("Architecture readiness", f"{score}%")
    b.metric("Checks needing detail", sum(r["Status"] != "Addressed" for r in audit))
    st.dataframe(pd.DataFrame(audit), use_container_width=True, hide_index=True)

    st.subheader("3. Reviewer stress test")
    for item in reviewer_challenges(plan):
        st.checkbox(item, key=f"exp_review_{item}")

    st.download_button("⬇️ Export experiment blueprint", export_architecture(plan, audit), "research_experiment_architecture.md", "text/markdown")

st.info("Integrity rule: the architect does not invent sample sizes, expected results, statistical significance, or causal conclusions. Complete the design with field-specific expertise and pre-specify decisions where appropriate.")
