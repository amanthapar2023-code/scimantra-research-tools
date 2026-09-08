import pandas as pd
import streamlit as st

from scimantra.falsification_lab import (
    audit_falsification,
    export_falsification,
    generate_alternatives,
    rank_discriminating_tests,
)

st.set_page_config(page_title="Falsification & Alternative-Hypothesis Lab | SciMantra", layout="wide")

st.title("Falsification & Alternative-Hypothesis Lab")
st.caption("Try to break your preferred explanation before you build the paper around it.")

st.warning(
    "Integrity rule: alternatives generated here are candidate explanations, not claims about your system. "
    "Hypothetical patterns and simulations must never be presented as experimental evidence."
)

# Reuse the experiment architect when this page is reached from the project workflow.
plan = st.session_state.get("experiment_plan", {})

def default(key, fallback):
    value = plan.get(key, "")
    return value if isinstance(value, str) and value.strip() else fallback

col1, col2 = st.columns(2)
with col1:
    hypothesis = st.text_area(
        "Primary hypothesis",
        value=default("Hypothesis", "The primary factor changes the primary outcome."),
        height=110,
    )
    factor = st.text_input("Primary factor / exposure", value=default("Primary factor / exposure", "the primary factor"))
    outcome = st.text_input("Primary outcome", value=default("Primary outcome", "the primary outcome"))
with col2:
    observed = st.text_area(
        "Observed or expected pattern",
        placeholder="Describe only what is actually observed, or clearly label it as expected/hypothetical.",
        height=110,
    )
    comparator = st.text_input("Comparator / reference", value=default("Comparator", "the comparator"))
    custom = st.text_area(
        "Your own alternative explanation (optional)",
        placeholder="Add a domain-specific competing explanation.",
        height=80,
    )

if st.button("Generate competing explanations", type="primary", use_container_width=True):
    rows = generate_alternatives(hypothesis, factor, outcome, comparator, observed)
    if custom.strip():
        rows.insert(
            0,
            {
                "Alternative explanation": "Researcher-defined alternative",
                "Candidate rationale": custom.strip(),
                "Primary hypothesis": hypothesis.strip(),
                "What it could explain": observed.strip() or "the observed pattern",
                "Discriminating test": "Researcher to specify a test that would distinguish this explanation from the primary hypothesis.",
                "Hypothetical pattern supporting alternative": "Researcher to specify",
                "Primary factor": factor.strip() or "the primary factor",
                "Primary outcome": outcome.strip() or "the primary outcome",
                "Comparator": comparator.strip() or "the comparator",
                "Control / measurement needed": "Researcher to specify",
                "Falsification status": "Unresolved",
                "Researcher decision / reason": "",
            },
        )
    st.session_state["falsification_rows"] = rows

rows = st.session_state.get("falsification_rows", [])
if rows:
    st.subheader("Competing explanations")
    st.caption("Edit the plan. The tool deliberately does not decide which explanation is correct.")

    for i, row in enumerate(rows):
        with st.expander(f"{i + 1}. {row['Alternative explanation']}", expanded=(i == 0)):
            row["Candidate rationale"] = st.text_area("Why this alternative is plausible", row["Candidate rationale"], key=f"alt_reason_{i}")
            row["Discriminating test"] = st.text_area("Discriminating test — what result would distinguish it?", row["Discriminating test"], key=f"alt_test_{i}")
            row["Hypothetical pattern supporting alternative"] = st.text_area(
                "Hypothetical pattern if the alternative were supported",
                row["Hypothetical pattern supporting alternative"],
                key=f"alt_pattern_{i}",
            )
            row["Control / measurement needed"] = st.text_input(
                "Control / measurement needed", row["Control / measurement needed"], key=f"alt_control_{i}"
            )
            row["Falsification status"] = st.selectbox(
                "Status",
                ["Unresolved", "Addressed", "Researcher rejected"],
                index=["Unresolved", "Addressed", "Researcher rejected"].index(row.get("Falsification status", "Unresolved")),
                key=f"alt_status_{i}",
            )
            row["Researcher decision / reason"] = st.text_area(
                "Decision / reason",
                row.get("Researcher decision / reason", ""),
                key=f"alt_decision_{i}",
            )

    audit = audit_falsification(rows)
    a, b, c, d = st.columns(4)
    a.metric("Alternatives", audit["alternatives"])
    b.metric("Audit score", f"{audit['audit_score']}%")
    c.metric("Unresolved", audit["unresolved"])
    d.metric("Status", audit["interpretation"])

    st.subheader("Highest-priority discriminating tests")
    st.dataframe(pd.DataFrame(rank_discriminating_tests(rows)), use_container_width=True, hide_index=True)

    st.subheader("Mind-change checkpoint")
    st.info("Before accepting a preferred explanation, write down: **Which result would change my mind?**")
    mind_change = st.text_area(
        "What result would change your mind?",
        key="falsification_mind_change",
        placeholder="Specify a measurable observation that would materially weaken or reject your preferred explanation.",
    )

    export = export_falsification(rows, audit) + f"\n## Mind-change checkpoint\n{mind_change.strip()}\n"
    st.download_button(
        "Download falsification plan (Markdown)",
        data=export,
        file_name="scimantra_falsification_plan.md",
        mime="text/markdown",
        use_container_width=True,
    )
else:
    st.info("Enter a hypothesis and generate competing explanations to start the falsification workflow.")
