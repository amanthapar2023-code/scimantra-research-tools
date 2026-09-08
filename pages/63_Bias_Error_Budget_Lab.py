import pandas as pd
import streamlit as st

from scimantra.bias_error_budget import budget_summary, build_budget, domain_rows, export_budget, mitigation_actions

st.set_page_config(page_title="Bias & Error Budget Lab | SciMantra", layout="wide")
st.title("Bias & Error Budget Lab")
st.caption("Find where a study is most vulnerable before those weaknesses become interpretation problems.")
st.warning("Integrity rule: scores are transparent planning heuristics, not measured bias, validity, effect size, or publication probability.")

rows = st.session_state.get("bias_budget_rows")
if rows is None:
    rows = domain_rows()
    st.session_state["bias_budget_rows"] = rows

st.subheader("1. Rate the vulnerability")
st.caption("Use your protocol knowledge. 0 = minimal concern / strong control; 5 = major concern / weak control.")

for i, row in enumerate(rows):
    with st.expander(row["Domain"], expanded=(i < 2)):
        st.write(row["Question"])
        row["Risk (0-5)"] = st.slider("Potential risk", 0, 5, int(row["Risk (0-5)"]), key=f"risk_{i}")
        row["Detectability (0-5)"] = st.slider("How difficult would it be to detect?", 0, 5, int(row["Detectability (0-5)"]), key=f"detect_{i}")
        row["Control strength (0-5)"] = st.slider("Current control strength", 0, 5, int(row["Control strength (0-5)"]), key=f"control_{i}")
        st.caption("Suggested mitigation")
        st.write(row["Mitigation"])
        row["Researcher evidence / notes"] = st.text_area("Evidence / protocol notes", row.get("Researcher evidence / notes", ""), key=f"notes_{i}")

budget = build_budget(rows)
summary = budget_summary(budget)

st.subheader("2. Residual-risk map")
a, b, c, d = st.columns(4)
a.metric("Overall index", f"{summary['overall']}")
b.metric("High priority", summary["high"])
c.metric("Moderate", summary["moderate"])
d.metric("Top vulnerability", summary["top_domain"] or "—")

st.dataframe(
    pd.DataFrame([
        {"Domain": r["Domain"], "Residual risk": r["Residual risk index"], "Priority": r["Priority"], "Risk": r["Risk (0-5)"], "Control": r["Control strength (0-5)"]}
        for r in budget
    ]),
    use_container_width=True,
    hide_index=True,
)

st.subheader("3. Mitigation queue")
actions = mitigation_actions(budget)
if actions:
    st.dataframe(pd.DataFrame(actions), use_container_width=True, hide_index=True)
else:
    st.success("No domain currently crosses the moderate residual-risk threshold under your inputs.")

st.info("Decision rule: address the highest residual-risk domains first, then document why any remaining risk is acceptable for the research question.")

st.download_button(
    "Download bias & error budget (Markdown)",
    export_budget(budget, summary),
    "scimantra_bias_error_budget.md",
    "text/markdown",
    use_container_width=True,
)
