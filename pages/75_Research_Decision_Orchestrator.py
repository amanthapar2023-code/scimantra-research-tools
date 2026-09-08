import pandas as pd
import streamlit as st
from src.scimantra.research_decision_orchestrator import template, orchestrate, action_queue, export_orchestration, LEVELS

st.set_page_config(page_title="Research Decision Orchestrator | SciMantra", page_icon="🧭", layout="wide")
st.title("🧭 Research Decision Orchestrator")
st.caption("Turn scattered research-audit findings into a prioritized next-action map.")
st.warning("Integrity rule: this orchestrator is decision support, not a scientific validity certificate or prediction of publication acceptance.")

if "decision_rows" not in st.session_state:
    st.session_state.decision_rows = template()

st.subheader("1. Integrate your research signals")
readiness = st.selectbox("Current project stage", ["Idea", "Experiment planning", "Data collection", "Analysis", "Discussion", "Manuscript", "Pre-submission"])
for i, row in enumerate(st.session_state.decision_rows):
    with st.expander(f"{i+1}. {row['Signal']} — {row['Status']}", expanded=i < 3):
        row["Status"] = st.selectbox("Status", LEVELS, index=LEVELS.index(row.get("Status", "Not assessed")), key=f"do_status_{i}")
        row["Evidence / module result"] = st.text_area("Evidence / result from relevant SciMantra module", row.get("Evidence / module result", ""), key=f"do_ev_{i}")
        row["Next action"] = st.selectbox("Next action", [row["Next action"]] + [x for x in ["Collect more evidence", "Add / improve control", "Change or re-check analysis", "Run validation experiment", "Test alternative explanation", "Verify prior art", "Weaken / narrow claim", "Improve reproducibility", "Proceed to manuscript", "Proceed to submission"] if x != row["Next action"]], key=f"do_action_{i}")

if st.button("🧭 Generate research decision map", type="primary", use_container_width=True):
    st.session_state.decision_summary = orchestrate(st.session_state.decision_rows, readiness)

summary = st.session_state.get("decision_summary")
if summary:
    st.divider()
    st.subheader("2. Decision dashboard")
    a,b,c,d = st.columns(4)
    a.metric("Integrated risk", f"{summary['risk']}/100")
    b.metric("Critical gaps", summary["critical"])
    c.metric("Needs work", summary["needs_work"])
    d.metric("Unassessed", summary["unassessed"])
    if summary["critical"]:
        st.error(f"**Recommended:** {summary['recommended_action']}")
    elif summary["needs_work"]:
        st.warning(f"**Recommended:** {summary['recommended_action']}")
    else:
        st.success(f"**Recommended:** {summary['recommended_action']}")

    if summary["critical_signals"]:
        st.write("**Critical signals:** " + ", ".join(summary["critical_signals"]))
    st.dataframe(pd.DataFrame(st.session_state.decision_rows), use_container_width=True, hide_index=True)

    st.subheader("3. Next-action queue")
    st.dataframe(pd.DataFrame(action_queue(st.session_state.decision_rows)), use_container_width=True, hide_index=True)
    st.download_button("⬇️ Export research decision map", export_orchestration(st.session_state.decision_rows, summary), "scimantra_research_decision_map.md", "text/markdown", use_container_width=True)
else:
    st.info("Set the status of each research signal, then generate the decision map.")

st.subheader("Decision principle")
st.write("**Do not optimize for 'publish now'. Optimize for resolving the strongest threat to the validity of the intended claim.**")
st.write("The orchestrator connects the logic of the SciMantra research suite: evidence → design → analysis → robustness → interpretation → claim → manuscript → submission.")
