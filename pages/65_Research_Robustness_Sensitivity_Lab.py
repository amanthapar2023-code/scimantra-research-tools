import pandas as pd
import streamlit as st

from scimantra.robustness_sensitivity import export_robustness, build_robustness_map, scenario_rows, stability_summary, fragile_scenarios

st.set_page_config(page_title="Research Robustness & Sensitivity | SciMantra", layout="wide")
st.title("Research Robustness & Sensitivity Lab")
st.caption("Stress-test the conclusion against reasonable analytical and design perturbations.")
st.warning("Integrity rule: this is a structured sensitivity audit. It does not prove that a conclusion is true or estimate robustness without appropriate data.")

rows = st.session_state.get("robustness_rows")
if rows is None:
    rows = scenario_rows()
    st.session_state["robustness_rows"] = rows

st.subheader("1. Record sensitivity checks")
st.caption("Enter results from checks you actually ran or mark them Not run. Do not invent robustness results.")

for i, row in enumerate(rows):
    with st.expander(row["Scenario"], expanded=(i < 2)):
        st.write(row["Perturbation"])
        st.caption(row["Question"])
        row["Direction preserved"] = st.selectbox(
            "Main conclusion direction",
            ["Unknown", "Unchanged", "Changed", "Reversed", "Not run"],
            index=["Unknown", "Unchanged", "Changed", "Reversed", "Not run"].index(str(row["Direction preserved"])),
            key=f"direction_{i}",
        )
        row["Effect magnitude change (%)"] = st.number_input(
            "Absolute change in main effect estimate (%)",
            min_value=0.0, max_value=1000.0, value=float(row["Effect magnitude change (%)"]), step=1.0, key=f"magnitude_{i}"
        )
        row["Confidence change"] = st.selectbox(
            "Inference / confidence change",
            ["Unknown", "Higher", "Unchanged", "Lower", "Crossed decision threshold", "Not run"],
            index=["Unknown", "Higher", "Unchanged", "Lower", "Crossed decision threshold", "Not run"].index(str(row["Confidence change"])),
            key=f"confidence_{i}",
        )
        row["Evidence / notes"] = st.text_area("Evidence / notes", row.get("Evidence / notes", ""), key=f"notes_{i}")

robustness = build_robustness_map(rows)
summary = stability_summary(robustness)

st.subheader("2. Conclusion Stability Map")
a, b, c, d = st.columns(4)
a.metric("Robustness score", f"{summary['robustness_score']}%")
b.metric("Assessed", summary["assessed"])
c.metric("Fragile", summary["Fragile"])
d.metric("Sensitive", summary["Sensitive"])

st.dataframe(pd.DataFrame([
    {"Scenario": r["Scenario"], "Stability": r["Stability"], "Direction": r["Direction preserved"], "Effect change %": r["Effect magnitude change (%)"], "Confidence": r["Confidence change"]}
    for r in robustness
]), use_container_width=True, hide_index=True)

st.subheader("3. Where the conclusion is vulnerable")
fragile = fragile_scenarios(robustness)
if fragile:
    st.dataframe(pd.DataFrame([
        {"Scenario": r["Scenario"], "Stability": r["Stability"], "Recommended response": "Investigate, document, and avoid overclaiming until the sensitivity is understood."}
        for r in fragile
    ]), use_container_width=True, hide_index=True)
else:
    st.success("No assessed scenario is currently classified as sensitive or fragile.")

st.info("A robust conclusion is not automatically a correct conclusion. Robustness means the interpretation survives the specific, scientifically defensible perturbations that were tested.")

st.download_button(
    "Download robustness audit (Markdown)",
    export_robustness(robustness, summary),
    "scimantra_robustness_sensitivity_audit.md",
    "text/markdown",
    use_container_width=True,
)
