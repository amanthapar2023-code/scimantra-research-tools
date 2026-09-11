import io
import numpy as np
import pandas as pd
import streamlit as st
from scipy import stats

st.title("🧬 Replicate-Aware Statistical Validation")
st.caption("V1.1 research validation: define the experimental unit before testing treatment effects.")

# Reuse the shared Data Analyzer dataset when available.
df = st.session_state.get("scimantra_research_df")
if df is None:
    uploaded = st.file_uploader("Upload Excel or CSV dataset", type=["xlsx", "xls", "csv"])
    if uploaded is not None:
        try:
            if uploaded.name.lower().endswith(".csv"):
                df = pd.read_csv(uploaded)
            else:
                book = pd.ExcelFile(uploaded)
                sheet = st.selectbox("Worksheet", book.sheet_names)
                df = pd.read_excel(uploaded, sheet_name=sheet)
        except Exception as exc:
            st.error(f"Could not read dataset: {exc}")
            st.stop()
if df is None or df.empty:
    st.info("Start in Data Analyzer or upload a dataset here.")
    st.stop()

df = df.copy()
numeric = df.select_dtypes(include=np.number).columns.tolist()
categorical = [c for c in df.columns if c not in numeric]

st.success(f"Dataset loaded: **{len(df):,} rows × {len(df.columns):,} columns**")

st.subheader("1. Define the experimental structure")
c1, c2, c3 = st.columns(3)
group = c1.selectbox("Treatment / group", ["—"] + categorical)
replicate = c2.selectbox("Experimental unit / replicate", ["—"] + categorical)
time = c3.selectbox("Time (optional)", ["—"] + categorical)
response = st.selectbox("Response variable", numeric if numeric else ["—"])

if group == "—" or replicate == "—" or response == "—":
    st.warning("Select a treatment/group, an experimental-unit identifier, and a numeric response before running validation.")
    st.stop()

work = df[[c for c in [group, replicate, time, response] if c != "—"]].copy()
work[response] = pd.to_numeric(work[response], errors="coerce")
work = work.dropna(subset=[group, replicate, response])

# Experimental-unit validation: repeated observations within the same unit are not
# treated as independent treatment replicates. If time is supplied, summarize it
# within unit × time first; otherwise summarize within unit.
keys = [group, replicate] + ([time] if time != "—" else [])
summary = work.groupby(keys, dropna=False)[response].agg(n_obs="size", mean="mean", sd=lambda x: x.std(ddof=1)).reset_index()
unit_summary = summary.groupby(group, dropna=False)["mean"].agg(n_units="size", mean="mean", sd=lambda x: x.std(ddof=1), sem=lambda x: x.std(ddof=1) / np.sqrt(x.notna().sum())).reset_index()

st.subheader("2. Experimental-unit quality gate")
counts = work.groupby([group, replicate], dropna=False).size().reset_index(name="observations")
repeated_units = int((counts["observations"] > 1).sum())
unit_counts = work.groupby(group, dropna=False)[replicate].nunique().reset_index(name="units")
issues = []
if repeated_units:
    issues.append(f"{repeated_units} experimental units contain repeated observations; raw rows should not be treated as independent replicates.")
if unit_counts["units"].min() < 2:
    issues.append("At least one group has fewer than 2 experimental units; inferential testing is not reliable for that group.")
if work[response].isna().sum():
    issues.append("Missing response values were excluded from the analysis.")
if issues:
    for issue in issues:
        st.warning(issue)
else:
    st.success("Quality gate passed: replicate identifiers are explicit and every group has at least two units.")

st.markdown("**Analysis rule:** inferential tests below use one summarized value per experimental unit (and per time point when time is selected), reducing pseudoreplication.")
st.dataframe(unit_summary, width="stretch")

st.subheader("3. Replicate-aware group comparison")
valid = unit_summary[unit_summary["n_units"] >= 2][group].tolist()
groups = [g for g in valid if pd.notna(g)]
if len(groups) < 2:
    st.info("At least two groups with ≥2 experimental units are needed for comparison.")
    st.stop()

arrays = [summary.loc[summary[group] == g, "mean"].dropna().to_numpy(dtype=float) for g in groups]
# For time-resolved data, unit-level summaries are still shown, but tests are based
# on all available unit × time observations and are explicitly labeled.
if len(groups) == 2:
    a, b = arrays[:2]
    t = stats.ttest_ind(a, b, equal_var=False)
    mw = stats.mannwhitneyu(a, b, alternative="two-sided")
    pooled = np.sqrt(((len(a)-1)*np.var(a, ddof=1) + (len(b)-1)*np.var(b, ddof=1)) / (len(a)+len(b)-2)) if len(a)+len(b)>2 else np.nan
    cohend = (np.mean(a)-np.mean(b))/pooled if pooled and np.isfinite(pooled) and pooled != 0 else np.nan
    out = pd.DataFrame([{"test":"Welch t-test","statistic":t.statistic,"p_value":t.pvalue},{"test":"Mann–Whitney U","statistic":mw.statistic,"p_value":mw.pvalue},{"test":"Cohen's d","statistic":cohend,"p_value":np.nan}])
else:
    an = stats.f_oneway(*arrays)
    kw = stats.kruskal(*arrays)
    out = pd.DataFrame([{"test":"One-way ANOVA","statistic":an.statistic,"p_value":an.pvalue},{"test":"Kruskal–Wallis","statistic":kw.statistic,"p_value":kw.pvalue}])

st.dataframe(out, width="stretch")

st.subheader("4. Assumption diagnostics")
diag = []
for g, arr in zip(groups, arrays):
    if len(arr) >= 3:
        sh = stats.shapiro(arr)
        diag.append({"group":g,"n_units":len(arr),"Shapiro W":sh.statistic,"normality p":sh.pvalue})
    else:
        diag.append({"group":g,"n_units":len(arr),"Shapiro W":np.nan,"normality p":np.nan})
if len(arrays) >= 2:
    lev = stats.levene(*arrays, center="median")
    st.metric("Levene variance p-value", f"{lev.pvalue:.5g}")
st.dataframe(pd.DataFrame(diag), width="stretch")

st.subheader("5. Validation report")
report = pd.DataFrame({"Item":["Rows supplied","Experimental units","Groups","Response","Grouping variable","Replicate variable","Time variable","Analysis principle"],"Value":[len(df),int(unit_summary["n_units"].sum()),len(groups),response,group,replicate,time,"One value per experimental unit; repeated observations are not counted as independent replicates."]})
st.dataframe(report, width="stretch")

csv = pd.concat([unit_summary.assign(_table="unit_summary"), out.assign(_table="statistics")], ignore_index=True, sort=False).to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Download validation results (CSV)", csv, "scimantra_replicate_validation.csv", "text/csv")

st.info("Scientific safeguard: statistical significance depends on the true experimental unit, study design, and assumptions. This engine provides transparent diagnostics; it does not certify a dataset as publication-ready.")
