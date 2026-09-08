import streamlit as st
import pandas as pd
from src.scimantra.design_optimizer import DESIGN_OPTIONS, optimize_design, improvement_actions, design_score, export_optimizer

st.set_page_config(page_title="Experimental Design Optimizer | SciMantra", page_icon="⚙️", layout="wide")
st.title("⚙️ Experimental Design Optimizer")
st.caption("Compare design choices and identify the highest-value improvements for validity, robustness, and reproducibility.")

selections = {}
cols = st.columns(2)
for i, (category, options) in enumerate(DESIGN_OPTIONS.items()):
    with cols[i % 2]:
        selections[category] = st.selectbox(category, options, index=min(1, len(options)-1), key=f"opt_{category}")
        selections[category] = options.index(selections[category])

if st.button("⚙️ Optimize design", type="primary"):
    st.session_state.optimizer_selections = selections

sel = st.session_state.get("optimizer_selections", selections)
rows = optimize_design(sel)
actions = improvement_actions(sel)

st.divider()
c1, c2 = st.columns(2)
c1.metric("Design robustness index", f"{design_score(sel)}%")
c2.metric("Potential improvements", len(actions))

st.subheader("1. Current design profile")
st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

st.subheader("2. Highest-value next improvements")
if actions:
    st.dataframe(pd.DataFrame(actions), use_container_width=True, hide_index=True)
    st.caption("The gain values are planning heuristics. They do not replace field-specific statistical design, power analysis, or expert review.")
else:
    st.success("All listed design dimensions are at their strongest built-in option.")

st.subheader("3. Decision rule")
st.info("Prefer the strongest design that is scientifically appropriate and feasible. Stronger controls, independent replication, randomization, blinding, measurement QC, pre-specified analysis, and reproducible records can reduce avoidable ambiguity—but they cannot rescue a poorly defined research question.")

st.download_button("⬇️ Export optimized design", export_optimizer(sel, rows, actions), "experimental_design_optimizer.md", "text/markdown")

st.info("Integrity rule: this optimizer does not claim that one design is universally best, does not calculate statistical power, and does not invent expected results. Use the existing Methodology Designer and Power Analysis tools for field-specific planning.")
