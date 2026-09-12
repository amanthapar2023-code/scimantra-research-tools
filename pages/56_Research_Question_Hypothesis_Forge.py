import streamlit as st
import pandas as pd
from src.scimantra.question_hypothesis_forge import (
    generate_questions,
    generate_hypotheses,
    audit_question,
    audit_design,
    audit_direction,
    export_forge,
)

st.set_page_config(page_title="Research Question & Hypothesis Forge | SciMantra", page_icon="❓", layout="wide")
st.title("❓ Research Question & Hypothesis Forge")
st.caption("Turn a verified gap into precise research questions, an evidence-aligned hypothesis, and a falsifiable experimental specification.")

st.subheader("1. Select the gap to investigate")
gap_text = st.text_area("Verified/working gap statement", placeholder="Describe the unresolved issue and the evidence that motivated it.")
gap_dimension = st.selectbox("Gap dimension", ["Evidence gap", "Method gap", "Population/context gap", "Technology gap", "Outcome gap", "Reproducibility gap", "Comparison gap"])
title = st.text_input("Research title / context", value=st.session_state.get("ri_title", ""))

if st.button("⚡ Forge research questions", type="primary"):
    gap = {"Gap dimension": gap_dimension, "Candidate research question": gap_text}
    st.session_state.forge_questions = generate_questions(gap, title)
    st.session_state.pop("forge_hypotheses", None)

questions = st.session_state.get("forge_questions", [])
if questions:
    st.divider()
    st.subheader("2. Candidate research questions")
    st.dataframe(pd.DataFrame(questions), use_container_width=True, hide_index=True)
    idx = st.selectbox("Question to develop", range(len(questions)), format_func=lambda i: f"{questions[i]['Type']}: {questions[i]['Research question'][:120]}")
    q = questions[idx]

    st.subheader("3. Make the question testable")
    edited = st.text_area("Edit selected question", value=q["Research question"], height=100)
    st.dataframe(pd.DataFrame(audit_question(edited)), use_container_width=True, hide_index=True)

    st.markdown("**Define the experimental roles before generating hypotheses**")
    c1, c2 = st.columns(2)
    with c1:
        primary = st.text_input("Primary intervention / exposure *", placeholder="e.g., microbial treatment")
        outcome = st.text_input("Primary outcome *", placeholder="e.g., percentage removal of target VOC (%)")
        comparator = st.text_input("Comparator / reference condition", placeholder="e.g., abiotic control without microbial treatment")
    with c2:
        secondary = st.text_input("Secondary factor / moderator", placeholder="e.g., initial VOC concentration")
        system = st.text_input("Population / experimental system *", placeholder="e.g., indoor-air microbial treatment system")
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

    if ready:
        st.subheader("Evidence-to-direction check")
        st.caption("SciMantra will not invent an expected direction. Choose a direction only when your literature, prior evidence, or explicit rationale supports it.")
        direction = st.radio("Expected direction for the primary hypothesis", ["Non-directional", "Higher", "Lower"], horizontal=True)
        direction_basis = st.text_area("Evidence basis for the direction (required for Higher/Lower)", placeholder="Briefly record the paper(s), prior findings, mechanism, pilot evidence, or other rationale supporting this direction.")
        dir_audit = pd.DataFrame(audit_direction(direction, direction_basis))
        st.dataframe(dir_audit, use_container_width=True, hide_index=True)

        if st.button("🧪 Forge hypothesis candidates", disabled=(direction.lower() != "non-directional" and not direction_basis.strip())):
            st.session_state.forge_hypotheses = generate_hypotheses(
                {"Research question": edited}, primary, outcome, comparator, secondary, system, conditions, direction, direction_basis
            )

    hypotheses = st.session_state.get("forge_hypotheses", [])
    if hypotheses:
        st.subheader("4. Evidence-aligned, falsifiable hypothesis candidates")
        st.dataframe(pd.DataFrame(hypotheses), use_container_width=True, hide_index=True)
        st.warning("These are testable planning candidates, not predictions of what your experiment will find. A directional claim requires a recorded evidence basis.")

        primary_h = next((h for h in hypotheses if h.get("Level") == "Primary"), hypotheses[0])
        selected_hypothesis = st.text_area("Hypothesis to carry forward", value=primary_h.get("Hypothesis", ""), key="forge_selected_hypothesis")
        selected_falsifier = st.text_area("Falsifier to carry forward", value=primary_h.get("Falsifier", ""), key="forge_selected_falsifier")

        if secondary.strip():
            st.info(f"Interaction logic: the hypothesis explicitly tests whether the effect of **{primary}** on **{outcome}** differs across levels of **{secondary}**.")

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
                "direction": direction,
                "direction_basis": direction_basis,
            }
            st.success("Plan prepared. Open Experiment Architect and click 'Import from Research Forge' to continue without re-entering these fields.")

        st.download_button("⬇️ Export question + hypothesis plan", export_forge(questions, hypotheses), "research_question_hypothesis_plan.md", "text/markdown")

st.info("Integrity rule: SciMantra does not manufacture expected results. Directional hypotheses require an evidence basis; otherwise the primary hypothesis remains non-directional. Variables, comparator, outcome, system, conditions, and falsifiers must be checked against the actual study design.")
