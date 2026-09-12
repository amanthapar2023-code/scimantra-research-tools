import streamlit as st
import pandas as pd
from src.scimantra.experiment_architect import (
    DESIGN_FIELDS, architect, audit_architecture, architecture_score,
    design_completion, design_specification, reviewer_challenges, export_architecture,
)

st.set_page_config(page_title="Research Experiment Architect | SciMantra", page_icon="🧪", layout="wide")
st.title("🧪 Research Experiment Architect")
st.caption("Convert a research question and hypothesis into an editable, auditable experimental blueprint.")

handoff = st.session_state.get("forge_handoff", {})
if handoff:
    st.success("Forge handoff available. The research question, hypothesis, experimental roles, system, and conditions can be imported below.")
    if st.button("📥 Import from Research Forge", type="primary"):
        st.session_state.exp_question = handoff.get("question", "")
        st.session_state.exp_hypothesis = handoff.get("hypothesis", "")
        st.session_state.exp_factor = handoff.get("primary", "")
        st.session_state.exp_outcome = handoff.get("outcome", "")
        st.session_state.exp_comparator = handoff.get("comparator", "")
        st.session_state.exp_secondary = handoff.get("secondary", "")
        st.session_state.exp_system = handoff.get("system", "")
        st.session_state.exp_conditions = handoff.get("conditions", "")
        st.session_state.exp_falsifier = handoff.get("falsifier", "")
        st.session_state.pop("forge_handoff", None)
        st.rerun()

question = st.text_area("Selected research question", value=st.session_state.get("exp_question", ""), placeholder="What exactly will this study test?", key="exp_question_input")
hypothesis = st.text_area("Selected hypothesis", value=st.session_state.get("exp_hypothesis", ""), placeholder="State the hypothesis and its potential falsifier.", key="exp_hypothesis_input")
c1, c2, c3 = st.columns(3)
factor = c1.text_input("Primary factor / exposure", value=st.session_state.get("exp_factor", ""), placeholder="Treatment, concentration, condition…", key="exp_factor_input")
outcome = c2.text_input("Primary outcome", value=st.session_state.get("exp_outcome", ""), placeholder="Measured endpoint + unit", key="exp_outcome_input")
comparator = c3.text_input("Comparator", value=st.session_state.get("exp_comparator", ""), placeholder="Control / reference condition", key="exp_comparator_input")
c4, c5, c6 = st.columns(3)
secondary = c4.text_input("Secondary factor / moderator", value=st.session_state.get("exp_secondary", ""), placeholder="e.g., initial VOC concentration", key="exp_secondary_input")
system = c5.text_input("Population / experimental system", value=st.session_state.get("exp_system", ""), placeholder="e.g., indoor-air microbial treatment system", key="exp_system_input")
conditions = c6.text_input("Key experimental conditions", value=st.session_state.get("exp_conditions", ""), placeholder="e.g., temperature, humidity, exposure duration", key="exp_conditions_input")
falsifier = st.text_area("Primary falsification criterion", value=st.session_state.get("exp_falsifier", ""), placeholder="What observation would count against the primary hypothesis?", height=80, key="exp_falsifier_input")

ready = bool(question.strip() and hypothesis.strip() and factor.strip() and outcome.strip() and system.strip() and conditions.strip())
if not ready:
    st.caption("Complete the question, hypothesis, primary factor, outcome, system, and key conditions before building the architecture.")
if st.button("🏗️ Build experiment architecture", type="primary", disabled=not ready):
    st.session_state.exp_question = question
    st.session_state.exp_hypothesis = hypothesis
    st.session_state.exp_factor = factor
    st.session_state.exp_outcome = outcome
    st.session_state.exp_comparator = comparator
    st.session_state.exp_secondary = secondary
    st.session_state.exp_system = system
    st.session_state.exp_conditions = conditions
    st.session_state.exp_falsifier = falsifier
    st.session_state.experiment_plan = architect(question, hypothesis, factor, outcome, comparator, secondary, system, conditions, falsifier)

plan = st.session_state.get("experiment_plan")
if plan:
    st.divider()
    st.subheader("1. Study architecture")
    editable = {}
    fixed_keys = {"Research question", "Hypothesis", "Primary factor / exposure", "Primary outcome", "Comparator", "Secondary factor / moderator", "Population / experimental system", "Key experimental conditions", "Falsification criterion"}
    for key, value in plan.items():
        editable[key] = st.text_area(key, value=str(value), height=90 if key not in fixed_keys else 80, key=f"exp_plan_{key}")
    plan.update(editable)
    st.session_state.experiment_plan = plan

    audit = audit_architecture(plan)
    score = architecture_score(audit)
    st.subheader("2. Design audit")
    a, b = st.columns(2)
    a.metric("Architecture readiness", f"{score}%")
    b.metric("Checks needing detail", sum(r["Status"] != "Addressed" for r in audit))
    st.dataframe(pd.DataFrame(audit), use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("3. Design Specification Builder")
    st.caption("Resolve audit gaps with researcher-defined decisions. SciMantra records what you specify; it does not invent sample sizes, controls, results, or statistical decisions.")
    saved = st.session_state.get("design_responses", {})
    responses = {}
    for i, (label, key, prompt) in enumerate(DESIGN_FIELDS):
        if i % 2 == 0:
            left, right = st.columns(2)
        target = left if i % 2 == 0 else right
        with target:
            responses[key] = st.text_area(label, value=saved.get(key, ""), placeholder=prompt, height=110, key=f"design_{key}")

    if st.button("💾 Save design specification", type="primary"):
        st.session_state.design_responses = responses
        st.session_state.experiment_plan = design_specification(plan, responses)
        st.rerun()

    plan = st.session_state.get("experiment_plan", plan)
    audit = audit_architecture(plan)
    completion = design_completion(audit)

    st.subheader("4. Design completion")
    overall = completion["overall"]
    st.progress(int(overall), text=f"Overall design completeness: {overall}%")
    group_items = list(completion["groups"].items())
    cols = st.columns(len(group_items))
    for col, (name, info) in zip(cols, group_items):
        col.metric(name, f"{info['percent']}%", f"{info['complete']}/{info['total']} addressed")

    if completion["analysis_ready"]:
        st.success("✅ Minimum design specification for analysis planning is recorded. Verify the protocol with field-specific expertise before data collection.")
        st.info("Next stage: statistical design can use the recorded experimental structure, measurement plan, and analysis decisions rather than guessing them.")
    else:
        blockers = ", ".join(completion["blocking_checks"])
        st.warning(f"Design is not ready for analysis planning. Resolve: {blockers}.")

    st.subheader("5. Reviewer stress test")
    st.caption("Tick a concern when it still needs resolution; ticking a box does not mark the design as solved.")
    for item in reviewer_challenges(plan):
        st.checkbox(item, key=f"exp_review_{item}")

    st.subheader("6. Updated blueprint")
    st.download_button("⬇️ Export complete experiment blueprint", export_architecture(plan, audit), "research_experiment_architecture.md", "text/markdown")

st.info("Integrity rule: the architect does not invent sample sizes, expected results, statistical significance, or causal conclusions. Complete the design with field-specific expertise and pre-specify decisions where appropriate.")
