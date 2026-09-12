import streamlit as st
import pandas as pd
from src.scimantra.question_hypothesis_forge import generate_questions, generate_hypotheses, audit_question, export_forge

st.set_page_config(page_title="Research Question & Hypothesis Forge | SciMantra", page_icon="❓", layout="wide")
st.title("❓ Research Question & Hypothesis Forge")
st.caption("Turn a verified gap hypothesis into precise research questions and falsifiable hypothesis candidates.")

st.subheader("1. Select the gap to investigate")
gap_text = st.text_area("Verified/working gap statement", placeholder="Describe the unresolved issue and the evidence that motivated it.")
gap_dimension = st.selectbox("Gap dimension", ["Evidence gap", "Method gap", "Population/context gap", "Technology gap", "Outcome gap", "Reproducibility gap", "Comparison gap"])
title = st.text_input("Research title / context", value=st.session_state.get("ri_title", ""))

if st.button("⚡ Forge research questions", type="primary"):
    gap = {"Gap dimension": gap_dimension, "Candidate research question": gap_text}
    st.session_state.forge_questions = generate_questions(gap, title)

questions = st.session_state.get("forge_questions", [])
if questions:
    st.divider()
    st.subheader("2. Candidate research questions")
    qdf = pd.DataFrame(questions)
    st.dataframe(qdf, use_container_width=True, hide_index=True)
    idx = st.selectbox("Question to develop", range(len(questions)), format_func=lambda i: f"{questions[i]['Type']}: {questions[i]['Research question'][:100]}")
    q = questions[idx]

    st.subheader("3. Make the question testable")
    edited = st.text_area("Edit selected question", value=q["Research question"], height=100)
    audit = audit_question(edited)
    st.dataframe(pd.DataFrame(audit), use_container_width=True, hide_index=True)

    c1, c2, c3 = st.columns(3)
    primary = c1.text_input("Primary factor / exposure", placeholder="e.g., VOC concentration")
    outcome = c2.text_input("Primary outcome", placeholder="e.g., percentage removal of target VOC")
    comparator = c3.text_input("Comparator", placeholder="e.g., abiotic control without microbial treatment")

    ready = bool(primary.strip() and outcome.strip())
    if not ready:
        st.caption("Enter at least the primary factor and primary outcome before generating hypotheses. Add a comparator when the study has a reference condition.")

    if st.button("🧪 Forge hypothesis candidates", disabled=not ready):
        st.session_state.forge_hypotheses = generate_hypotheses({"Research question": edited}, primary, outcome, comparator)

    hypotheses = st.session_state.get("forge_hypotheses", [])
    if hypotheses:
        st.subheader("4. Falsifiable hypothesis candidates")
        st.dataframe(pd.DataFrame(hypotheses), use_container_width=True, hide_index=True)
        st.warning("These are testable planning candidates, not predictions of what your experiment will find. Pre-specify outcomes, analysis, and falsification criteria before interpreting results.")
        st.download_button("⬇️ Export question + hypothesis plan", export_forge(questions, hypotheses), "research_question_hypothesis_plan.md", "text/markdown")

st.info("Integrity rule: SciMantra does not manufacture expected results. A hypothesis is useful here only when its variables, comparator, outcome, and potential falsifier can be defined and checked against the study design.")
