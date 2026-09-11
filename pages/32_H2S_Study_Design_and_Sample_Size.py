import numpy as np
import pandas as pd
import streamlit as st
from scipy import stats

st.title("🧪 H₂S Study Design & Sample Size Planner")
st.caption("Plan defensible experiments before collecting data: experimental units, balance, effect size and power.")

st.subheader("1. Define the study")
c1, c2, c3 = st.columns(3)
design = c1.selectbox("Design", ["Two independent groups", "One-way multiple groups", "Paired measurements"])
alpha = c2.number_input("Significance level (α)", min_value=0.001, max_value=0.20, value=0.05, step=0.01)
power = c3.number_input("Target power", min_value=0.50, max_value=0.99, value=0.80, step=0.05)

st.subheader("2. Estimate the expected effect")
if design == "Two independent groups":
    c1, c2, c3 = st.columns(3)
    mean1 = c1.number_input("Expected mean — group 1", value=80.0)
    mean2 = c2.number_input("Expected mean — group 2", value=60.0)
    sd = c3.number_input("Expected common SD", min_value=1e-9, value=15.0)
    d = abs(mean1 - mean2) / sd
    st.metric("Standardized effect (Cohen's d)", f"{d:.3f}")
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_power = stats.norm.ppf(power)
    n_each = int(np.ceil(2 * (z_alpha + z_power) ** 2 / max(d, 1e-12) ** 2))
    st.metric("Approximate units per group", n_each)
    st.info("This is a planning approximation for a two-sided independent-groups comparison. Inflate for expected attrition, unusable samples or prespecified multiple-comparison adjustments.")
elif design == "One-way multiple groups":
    c1, c2 = st.columns(2)
    k = c1.number_input("Number of groups", min_value=3, max_value=20, value=4, step=1)
    f = c2.number_input("Expected Cohen's f", min_value=0.01, max_value=2.0, value=0.30, step=0.05)
    # Practical approximation based on the noncentral F distribution solved by grid search.
    target = power
    candidates = []
    for n in range(k * 2, k * 200 + 1):
        df1 = k - 1
        df2 = n - k
        crit = stats.f.ppf(1 - alpha, df1, df2)
        if not np.isfinite(crit):
            continue
        nc = n * f * f
        achieved = stats.ncf.sf(crit, df1, df2, nc)
        if achieved >= target:
            candidates.append((n, achieved))
            break
    if candidates:
        total, achieved = candidates[0]
        st.metric("Approximate total experimental units", total)
        st.metric("Approximate power", f"{achieved:.3f}")
        st.info("The planner searches total units across groups and assumes a balanced one-way design. Confirm the final design with the exact analysis model and planned contrasts.")
    else:
        st.warning("Increase the search range or use a smaller effect size only with strong scientific justification.")
else:
    c1, c2, c3 = st.columns(3)
    mean_diff = c1.number_input("Expected paired mean difference", value=10.0)
    sd_diff = c2.number_input("SD of paired differences", min_value=1e-9, value=15.0)
    ratio = c3.number_input("Expected usable fraction", min_value=0.10, max_value=1.0, value=0.90, step=0.05)
    dz = abs(mean_diff) / sd_diff
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_power = stats.norm.ppf(power)
    usable = int(np.ceil((z_alpha + z_power) ** 2 / max(dz, 1e-12) ** 2))
    recruited = int(np.ceil(usable / ratio))
    st.metric("Standardized paired effect (dz)", f"{dz:.3f}")
    st.metric("Approximate usable pairs", usable)
    st.metric("Recruit/collect approximately", recruited)

st.subheader("3. Experimental-unit rules")
for text in [
    "Define the independent experimental unit before data collection.",
    "Do not count technical repeats or repeated time points as independent biological/experimental replicates.",
    "Randomize treatment assignment where feasible and prespecify exclusions.",
    "Record treatment, experimental-unit ID, time, batch and key covariates.",
    "Plan the primary endpoint and statistical model before inspecting treatment outcomes.",
]:
    st.checkbox(text, value=True)

st.subheader("4. Planning table")
plan = pd.DataFrame([
    ["Design", design],
    ["Alpha", alpha],
    ["Target power", power],
    ["Primary independent unit", "Biological/experimental unit"],
    ["Technical repeats", "Not independent replicates"],
    ["Time points", "Repeated measures unless independently randomized"],
], columns=["Planning item", "Value"])
st.dataframe(plan, width="stretch")
st.download_button("⬇️ Download study plan (CSV)", plan.to_csv(index=False).encode("utf-8"), "scimantra_h2s_study_plan.csv", "text/csv")
st.warning("Planning estimates depend on the true effect, variability, design, and analysis model. Treat the calculated sample size as a planning aid, not a guarantee of publication power.")
