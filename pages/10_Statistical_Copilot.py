import io
from datetime import datetime

import numpy as np
import pandas as pd
import streamlit as st
from scipy import stats

from src.scimantra.entitlements import require

st.set_page_config(page_title="SciMantra Statistical Copilot", page_icon="🧠", layout="wide")
st.title("🧠 SciMantra Statistical Copilot")
st.caption("Deterministic statistical analysis for research datasets, with transparent assumptions and publication-ready drafts.")

if not require("statistical_copilot"):
    st.stop()

if "copilot_df" not in st.session_state:
    st.session_state.copilot_df = None

uploaded = st.file_uploader("Upload CSV or Excel dataset", type=["csv", "xlsx", "xls"])
if uploaded:
    try:
        st.session_state.copilot_df = pd.read_csv(uploaded) if uploaded.name.lower().endswith(".csv") else pd.read_excel(uploaded)
    except Exception as exc:
        st.error(f"Could not read dataset: {exc}")

df = st.session_state.copilot_df
if df is None:
    st.info("Upload an experimental dataset to begin.")
    st.stop()

st.success(f"Loaded {len(df):,} observations × {len(df.columns):,} variables")
numeric_cols = list(df.select_dtypes(include="number").columns)
if len(numeric_cols) < 1:
    st.warning("At least one numeric variable is required for quantitative tests.")
    st.stop()

st.subheader("1. Explore the variables")
col1, col2 = st.columns(2)
y = col1.selectbox("Outcome / response variable", numeric_cols)
groups = [c for c in df.columns if c != y]
group_col = col2.selectbox("Grouping / treatment variable (optional)", ["None"] + groups)
clean_y = pd.to_numeric(df[y], errors="coerce")
st.write(f"**{y}**: n={clean_y.notna().sum():,}, mean={clean_y.mean():.5g}, SD={clean_y.std():.5g}, median={clean_y.median():.5g}")

if group_col != "None":
    work = pd.DataFrame({"y": clean_y, "group": df[group_col]}).dropna()
    group_stats = work.groupby("group", dropna=True)["y"].agg(["count", "mean", "std", "median", "min", "max"]).reset_index()
    st.dataframe(group_stats.round(6), width="stretch", hide_index=True)
    if len(group_stats) >= 2:
        st.subheader("2. Group comparison")
        test = st.selectbox("Test", ["Welch t-test (2 groups)", "Mann–Whitney U (2 groups)", "One-way ANOVA (2+ groups)", "Kruskal–Wallis (2+ groups)"])
        arrays = [g["y"].to_numpy(dtype=float) for _, g in work.groupby("group") if len(g) >= 2]
        names = [str(k) for k, g in work.groupby("group") if len(g) >= 2]
        result = None
        if st.button("Run statistical test", type="primary"):
            if len(arrays) < 2:
                st.error("At least two groups with two observations each are required.")
            elif "Welch" in test or "Mann" in test:
                if len(arrays) != 2:
                    st.error("This test requires exactly two valid groups.")
                elif "Welch" in test:
                    stat, p = stats.ttest_ind(arrays[0], arrays[1], equal_var=False, nan_policy="omit")
                    result = ("Welch t-test", stat, p)
                else:
                    stat, p = stats.mannwhitneyu(arrays[0], arrays[1], alternative="two-sided")
                    result = ("Mann–Whitney U", stat, p)
            elif "ANOVA" in test:
                stat, p = stats.f_oneway(*arrays)
                result = ("One-way ANOVA", stat, p)
            else:
                stat, p = stats.kruskal(*arrays)
                result = ("Kruskal–Wallis", stat, p)
            if result:
                test_name, statistic, pvalue = result
                st.metric("p-value", f"{pvalue:.6g}")
                st.write(f"**{test_name}**: statistic={statistic:.6g}, p={pvalue:.6g}.")
                if pvalue < 0.05:
                    st.success("The selected test indicates evidence against the null hypothesis at α=0.05.")
                else:
                    st.info("The selected test does not provide evidence against the null hypothesis at α=0.05.")
                st.warning("A p-value alone does not establish biological importance or causality. Check assumptions, effect size, replication and study design.")
                st.session_state["copilot_result"] = {"test": test_name, "statistic": float(statistic), "pvalue": float(pvalue), "outcome": str(y), "group": str(group_col), "groups": names}

st.subheader("3. Association / regression")
if len(numeric_cols) >= 2:
    x = st.selectbox("Predictor variable", [c for c in numeric_cols if c != y])
    pair = pd.DataFrame({"x": pd.to_numeric(df[x], errors="coerce"), "y": clean_y}).dropna()
    if len(pair) >= 3 and st.button("Calculate correlation and linear regression"):
        pearson_r, pearson_p = stats.pearsonr(pair["x"], pair["y"])
        spearman_r, spearman_p = stats.spearmanr(pair["x"], pair["y"])
        slope, intercept, rvalue, pvalue, stderr = stats.linregress(pair["x"], pair["y"])
        c1, c2, c3 = st.columns(3)
        c1.metric("Pearson r", f"{pearson_r:.4f}")
        c2.metric("Spearman ρ", f"{spearman_r:.4f}")
        c3.metric("Regression R²", f"{rvalue**2:.4f}")
        st.write(f"Linear model: **{y} = {intercept:.5g} + ({slope:.5g}) × {x}**; regression p={pvalue:.6g}, SE(slope)={stderr:.5g}.")
        st.warning("Association is not proof of causation. Inspect residuals, leverage/outliers and experimental design before interpreting a regression biologically.")

st.subheader("4. Results draft")
res = st.session_state.get("copilot_result")
if res:
    direction = "statistically significant evidence" if res["pvalue"] < 0.05 else "no statistically significant evidence"
    draft = (f"A {res['test']} was conducted to compare {res['outcome']} across {res['group']} groups ({', '.join(res['groups'])}). The analysis yielded a test statistic of {res['statistic']:.4g} and p={res['pvalue']:.4g}, indicating {direction} of a difference at α=0.05. These findings should be interpreted alongside effect sizes, confidence intervals, replicate structure, assumption checks and the biological context of the experiment.")
    st.text_area("Editable Results paragraph", draft, height=180)
    st.download_button("⬇️ Download Results draft", draft, "scimantra_results_draft.txt", "text/plain")
else:
    st.info("Run a group comparison above to generate a grounded Results paragraph.")

st.caption(f"Analysis generated {datetime.now().strftime('%Y-%m-%d %H:%M')}. Statistical output is computational evidence, not a substitute for study-design review or domain expertise.")
