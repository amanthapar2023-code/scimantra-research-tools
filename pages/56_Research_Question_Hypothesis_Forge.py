import streamlit as st
import pandas as pd
from src.scimantra.question_hypothesis_forge import (
    generate_questions,
    generate_hypotheses,
    audit_question,
    audit_design,
    export_forge,
)

st.set_page_config(page_title="Research Question & Hypothesis Forge | SciMantra", page_icon="❓", layout="wide")
st.title("❓ Research Question & Hypothesis Forge")
st.caption("Turn a verified gap into precise research questions, a coherent experimental specification, and falsifiable hypothesis candidates.")

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
    st.dataframe(pd.DataFrame(questions), use_container_width=True, hide_index=True)
    idx = st.selectbox("Question to develop", range(len(questions)), format_func=lambda i: f"{questions[i]['Type']}: {questions[i]['Research question'][:100]}")
    q = questions[idx]

    st.subheader("3. Make the question testable")
    edited = st.text_area("Edit selected question", value=q["Research question"], height=100)
    st.dataframe(pd.DataFrame(audit_question(edited)), use_container_width=True, hide_index=True)

    st.markdown("**Define the experimental roles before generating hypotheses**")
    c1, c2 = st.columns(2)
    with c1:
        primary = st.text_input("Primary intervention / exposure *", placeholder="e.g., microbial treatment or VOC concentration")
        outcome = st.text_input("Primary outcome *", placeholder="e.g., percentage removal of target VOC")
        comparator = st.text_input("Comparator / reference condition", placeholder="e.g., abiotic control without microbial treatment")
    with c2:
        secondary = st.text_input("Secondary factor / moderator", placeholder="e.g., initial VOC concentration")
        system = st.text_input("Population / experimental system *", placeholder="e.g., indoor-air microbial bioreactor")
        conditions = st.text_input("Key experimental conditions *", placeholder="e.g., temperature, humidity, exposure duration")

    ready = bool(primary.strip() and outcome.strip() and system.strip() and conditions.strip())
    if not ready:
        st.caption("Required: primary intervention/exposure, primary outcome, population/system, and key conditions. Add a comparator when the study has a reference condition.")

    if st.button("🔎 Audit experimental specification"):
        st.session_state.forge_design_audit = audit_design(primary, outcome, comparator, secondary, system, conditions)

    design_audit = st.session_state.get("forge_design_audit", [])
    if design_audit:
        st.subheader("Experimental specification audit")
        adf = pd.DataFrame(design_audit)
        st.dataframe(adf, use_container_width=True, hide_index=True)
        mismatch = adf[adf["Status"] == "Review"]
        if not mismatch.empty:
            st.warning("Review the flagged role mismatch before treating the hypothesis as a coherent experimental plan.")
        elif all(adf["Status"].isin(["Present", "Optional", "No obvious mismatch"])):
            st.success("No obvious role mismatch detected. Verify the specification against the actual protocol before proceeding.")

    if st.button("🧪 Forge hypothesis candidates", disabled=not ready):
        st.session_state.forge_hypotheses = generate_hypotheses(
            {"Research question": edited}, primary, outcome, comparator, secondary, system, conditions
        )
        st.session_state.forge_handoff = {
            "question": edited,
            "hypothesis": "",
            "primary": primary,
            "outcome": outcome,
            "comparator": comparator,
            "secondary": secondary,
            "system": system,
            "conditions": conditions,
            "falsifier": "",
        }

    hypotheses = st.session_state.get("forge_hypotheses", [])
    if hypotheses:
        st.subheader("4. Falsifiable hypothesis candidates")
        st.dataframe(pd.DataFrame(hypotheses), use_container_width=True, hide_index=True)
        st.warning("These are testable planning candidates, not predictions of what your experiment will find. Pre-specify outcomes, analysis, and falsification criteria before interpreting results.")

        directional = next((h for h in hypotheses if h.get("Level") == "Directional"), hypotheses[0])
        selected_hypothesis = st.text_area("Hypothesis to carry forward", value=directional.get("Hypothesis", ""), key="forge_selected_hypothesis")
        selected_falsifier = st.text_area("Falsifier to carry forward", value=directional.get("Falsifier", ""), key="forge_selected_falsifier")

        if st.button("➡️ Send this plan to Experiment Architect", type="primary"):
            st.session_state.forge_handoff = {
                "question": edited,
                "hypothesis": selected_hypothesis,
                "primary": primary,
                "outcome": outcome,
                "comparator": comparator,
                "secondary": secondary,
                "system": system,
                "conditions": conditions,
                "falsifier": selected_falsifier,
            }
            st.success("Plan prepared. Open Experiment Architect and click 'Import from Research Forge' to continue without re-entering these fields.")

        st.download_button("⬇️ Export question + hypothesis plan", export_forge(questions, hypotheses), "research_question_hypothesis_plan.md", "text/markdown")

st.info("Integrity rule: SciMantra does not manufacture expected results. A hypothesis is useful here only when its variables, comparator, outcome, system, conditions, and potential falsifier can be defined and checked against the study design.")
