import math
from datetime import datetime

import numpy as np
import pandas as pd
import streamlit as st
from scipy import stats

st.set_page_config(page_title="SciMantra Experimental Design", page_icon="🧪", layout="wide")
st.title("🧪 Experimental Design & Power Analysis")
st.caption("Plan experiments before collecting data: sample size, power, effect size, randomization and design checks.")

mode = st.selectbox("Planning module", [
    "Two-group sample size",
    "Two-group power",
    "Effect size from pilot data",
    "Randomization planner",
    "Experimental design checklist",
])

if mode == "Two-group sample size":
    st.subheader("Estimate sample size for two independent groups")
    effect = st.number_input("Expected Cohen's d", min_value=0.05, value=0.5, step=0.05)
    alpha = st.number_input("Alpha (two-sided)", min_value=0.001, max_value=0.20, value=0.05, step=0.01)
    power = st.number_input("Target power", min_value=0.50, max_value=0.999, value=0.80, step=0.05)
    if st.button("Calculate sample size", type="primary"):
        z_alpha = stats.norm.ppf(1 - alpha / 2)
        z_beta = stats.norm.ppf(power)
        n = math.ceil(2 * ((z_alpha + z_beta) / effect) ** 2)
        st.metric("Approx. observations per group", n)
        st.write(f"Approximate total sample size: **{2*n}** observations.")
        st.info("This is an analytical approximation for two independent groups with a standardized continuous outcome. Attrition, clustering, repeated measures and unequal allocation can change the required sample size.")

elif mode == "Two-group power":
    st.subheader("Estimate power for a planned two-group comparison")
    n = st.number_input("Observations per group", min_value=2, value=10, step=1)
    effect = st.number_input("Expected Cohen's d", min_value=0.01, value=0.5, step=0.05)
    alpha = st.number_input("Alpha", min_value=0.001, max_value=0.20, value=0.05, step=0.01)
    if st.button("Calculate power", type="primary"):
        delta = effect * math.sqrt(n / 2)
        critical = stats.norm.ppf(1 - alpha / 2)
        power = stats.norm.cdf(-critical - delta) + 1 - stats.norm.cdf(critical - delta)
        st.metric("Approx. power", f"{power:.3%}")
        if power < 0.80:
            st.warning("Planned power is below 80%. Consider increasing replication or reassessing the expected effect size.")
        else:
            st.success("Planned power is at or above 80% under the stated assumptions.")

elif mode == "Effect size from pilot data":
    st.subheader("Calculate standardized effect size from pilot measurements")
    a = st.text_area("Group A values", placeholder="12, 14, 13, 15, 16")
    b = st.text_area("Group B values", placeholder="10, 11, 9, 12, 10")
    if st.button("Calculate effect size", type="primary"):
        try:
            va = np.array([float(x.strip()) for x in a.replace(";", ",").split(",") if x.strip()])
            vb = np.array([float(x.strip()) for x in b.replace(";", ",").split(",") if x.strip()])
            if len(va) < 2 or len(vb) < 2:
                raise ValueError("Each group needs at least two observations.")
            pooled = math.sqrt(((len(va)-1)*va.var(ddof=1) + (len(vb)-1)*vb.var(ddof=1)) / (len(va)+len(vb)-2))
            d = (va.mean() - vb.mean()) / pooled if pooled > 0 else np.nan
            correction = 1 - 3 / (4*(len(va)+len(vb))-9)
            hedges_g = d * correction
            st.metric("Cohen's d", f"{d:.4f}")
            st.metric("Hedges' g", f"{hedges_g:.4f}")
            st.caption("Effect-size magnitude should be interpreted in the scientific context; generic small/medium/large labels are not universal.")
        except Exception as exc:
            st.error(f"Could not calculate effect size: {exc}")

elif mode == "Randomization planner":
    st.subheader("Create a reproducible treatment allocation")
    groups_text = st.text_input("Groups and target counts", "Control:6, Treatment A:6, Treatment B:6")
    seed = st.number_input("Random seed", min_value=0, value=2026, step=1)
    if st.button("Generate allocation", type="primary"):
        try:
            parts = [p.strip() for p in groups_text.split(",") if p.strip()]
            labels, counts = [], []
            for part in parts:
                name, count = part.rsplit(":", 1)
                labels.append(name.strip())
                counts.append(int(count.strip()))
            allocation = [name for name, count in zip(labels, counts) for _ in range(count)]
            rng = np.random.default_rng(int(seed))
            rng.shuffle(allocation)
            plan = pd.DataFrame({"Experimental_unit": np.arange(1, len(allocation)+1), "Treatment": allocation})
            st.dataframe(plan, width="stretch", hide_index=True)
            st.download_button("⬇️ Download randomization plan", plan.to_csv(index=False).encode("utf-8"), "scimantra_randomization_plan.csv", "text/csv")
            st.info("Keep the random seed and allocation record with the study documentation. Randomization does not replace appropriate blocking or stratification when those are required by the design.")
        except Exception as exc:
            st.error(f"Could not create allocation: {exc}")

else:
    st.subheader("Experimental design checklist")
    items = [
        "Define the primary research question and primary outcome before data collection.",
        "Identify the true experimental unit; technical replicates are not automatically independent biological replicates.",
        "Predefine treatment groups, controls and inclusion/exclusion criteria.",
        "Choose biological replication based on expected variability and scientifically meaningful effect size.",
        "Randomize assignment where feasible and document the randomization method.",
        "Consider blocking/stratification when batch, day, operator or other nuisance factors may influence outcomes.",
        "Predefine the statistical model and primary comparison where possible.",
        "Plan how missing observations, outliers and failed experiments will be handled.",
        "Avoid increasing sample size solely because an interim p-value is inconvenient unless a valid sequential design was planned.",
        "Record protocol deviations and preserve an auditable analysis dataset.",
    ]
    for i, item in enumerate(items):
        st.checkbox(item, key=f"design_{i}")
    if st.button("Generate planning record"):
        checked = [items[i] for i in range(len(items)) if st.session_state.get(f"design_{i}")]
        record = "SciMantra Experimental Design Planning Record\n" + "="*40 + "\n" + f"Generated: {datetime.now():%Y-%m-%d %H:%M}\n\n"
        record += "Completed checklist:\n" + "\n".join(f"- {x}" for x in checked) + "\n\n"
        record += "Uncompleted checklist:\n" + "\n".join(f"- {items[i]}" for i in range(len(items)) if not st.session_state.get(f"design_{i}"))
        st.download_button("⬇️ Download planning record", record.encode("utf-8"), "scimantra_experimental_design_record.txt", "text/plain")

st.divider()
st.warning("Power and sample-size calculations depend on study design and assumptions. Treat these outputs as planning estimates and obtain appropriate statistical/design review for complex experiments, clustered data, repeated measures, survival outcomes, or nonstandard endpoints.")
