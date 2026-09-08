import pandas as pd
import streamlit as st

from scimantra.statistical_assumptions import analysis_options, audit_summary, build_audit, default_checks, export_audit

st.set_page_config(page_title="Statistical Assumption Lab | SciMantra", layout="wide")
st.title("Statistical Assumption & Analysis-Choice Lab")
st.caption("Record why an analysis fits the research question and expose assumption risks before interpretation.")
st.warning("This is a planning and audit aid. It does not certify statistical assumptions, guarantee validity, or automatically choose the correct analysis.")

c1, c2 = st.columns(2)
with c1:
    research_question = st.text_area("Research question / estimand", placeholder="What quantity or comparison are you trying to estimate?")
    outcome = st.text_input("Primary outcome", placeholder="e.g., concentration, growth rate, binary response")
with c2:
    design = st.selectbox("Study / data structure", ["Independent groups", "Paired / repeated measures", "Longitudinal", "Count outcome", "Binary outcome", "Other"])
    analysis_choice = st.selectbox("Proposed analysis", analysis_options(design))

if "stat_assumption_rows" not in st.session_state:
    st.session_state["stat_assumption_rows"] = default_checks()
rows = st.session_state["stat_assumption_rows"]

st.subheader("1. Pre-analysis assumption audit")
st.caption("Concern: 0 = little concern, 5 = major concern. Readiness: 0 = not addressed, 5 = strongly addressed.")
for i, row in enumerate(rows):
    with st.expander(row["Check"], expanded=(i < 3)):
        st.write(row["Question"])
        row["Concern (0-5)"] = st.slider("Potential concern", 0, 5, int(row["Concern (0-5)"]), key=f"sa_c_{i}")
        row["Readiness (0-5)"] = st.slider("Current readiness", 0, 5, int(row["Readiness (0-5)"]), key=f"sa_r_{i}")
        st.caption("Recommended action")
        st.write(row["Recommended action"])
        row["Decision record"] = st.text_area("Your decision / evidence", row.get("Decision record", ""), key=f"sa_n_{i}")

audit = build_audit(rows)
summary = audit_summary(audit)

st.subheader("2. Analysis-risk dashboard")
a, b, c, d = st.columns(4)
a.metric("Overall index", summary["overall"])
b.metric("High priority", summary["high"])
c.metric("Moderate", summary["moderate"])
d.metric("Top issue", summary["top"] or "—")

st.dataframe(pd.DataFrame([{"Check": r["Check"], "Risk index": r["Analysis-risk index"], "Priority": r["Priority"], "Concern": r["Concern (0-5)"], "Readiness": r["Readiness (0-5)"]} for r in audit]), use_container_width=True, hide_index=True)

st.subheader("3. Analysis decision record")
st.write(f"**Research question:** {research_question or 'Not entered'}")
st.write(f"**Primary outcome:** {outcome or 'Not entered'}")
st.write(f"**Design:** {design}")
st.write(f"**Proposed analysis:** {analysis_choice}")
if summary["high"]:
    st.error("Do not treat the analysis choice as settled yet: high-priority assumption or design issues remain.")
else:
    st.success("No high-priority analysis-risk issue under the current researcher ratings. Document the rationale and verify assumptions with the actual data.")

st.download_button("Download pre-analysis decision record (Markdown)", export_audit(audit, summary, analysis_choice), "scimantra_statistical_decision_record.md", "text/markdown", use_container_width=True)
