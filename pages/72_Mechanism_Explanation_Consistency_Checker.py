import pandas as pd
import streamlit as st
from src.scimantra.mechanism_consistency import template_rows, audit, priority_queue, export_audit, LEVELS

st.set_page_config(page_title="Mechanism Consistency | SciMantra", page_icon="🧬", layout="wide")
st.title("🧬 Mechanism / Explanation Consistency Checker")
st.caption("Stress-test whether the mechanism or explanation in your Discussion is actually supported by what you measured.")
st.warning("Integrity rule: association does not automatically establish mechanism or causation. This tool helps expose unsupported explanatory steps; it does not discover or prove a mechanism.")

if "mechanism_rows" not in st.session_state:
    st.session_state.mechanism_rows = template_rows()

claim = st.text_area("Exact mechanistic / explanatory claim", height=110, placeholder="Example: X improves Y because it activates pathway Z.")

st.subheader("1. Mechanism evidence audit")
for i, row in enumerate(st.session_state.mechanism_rows):
    with st.expander(f"{i+1}. {row['Domain']} — {row['Assessment']}", expanded=i < 3):
        row["Assessment"] = st.selectbox("Assessment", LEVELS, index=LEVELS.index(row.get("Assessment", "Not assessed")), key=f"mc_assess_{i}")
        row["Evidence"] = st.text_area("What evidence supports or challenges this?", row.get("Evidence", ""), key=f"mc_ev_{i}")
        row["Alternative explanation"] = st.text_input("Alternative explanation", row.get("Alternative explanation", ""), key=f"mc_alt_{i}")
        row["Notes"] = st.text_area("Researcher notes / boundary", row.get("Notes", ""), key=f"mc_notes_{i}")

if st.button("🧬 Run mechanism consistency audit", type="primary", use_container_width=True):
    st.session_state.mechanism_summary = audit(st.session_state.mechanism_rows)

summary = st.session_state.get("mechanism_summary")
if summary:
    st.divider()
    st.subheader("2. Mechanism consistency dashboard")
    a,b,c,d = st.columns(4)
    a.metric("Domains assessed", summary["assessed"])
    b.metric("Planning score", f"{summary['score']}/100")
    c.metric("Consistent", summary["Consistent"])
    d.metric("Weak / contradictory", summary["Weak / indirect"] + summary["Contradictory"])
    st.dataframe(pd.DataFrame(st.session_state.mechanism_rows), use_container_width=True, hide_index=True)

    st.subheader("3. Highest-risk explanatory gaps")
    st.dataframe(pd.DataFrame(priority_queue(st.session_state.mechanism_rows)), use_container_width=True, hide_index=True)
    st.download_button("⬇️ Export mechanism audit", export_audit(st.session_state.mechanism_rows, summary), "scimantra_mechanism_consistency_audit.md", "text/markdown", use_container_width=True)

st.subheader("Reviewer questions")
for q in [
    "Which part of the proposed mechanism was actually measured?",
    "What observation distinguishes the proposed mechanism from competing explanations?",
    "Does the mechanism occur in the required temporal order?",
    "Was the mechanism perturbed, blocked, rescued, or otherwise challenged?",
    "Could the same endpoint arise through a different pathway?",
    "Should the manuscript say 'consistent with' rather than 'demonstrates' or 'causes'?",
]:
    st.write("• " + q)
