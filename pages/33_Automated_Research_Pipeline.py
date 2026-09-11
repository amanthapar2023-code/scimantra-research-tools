import io
import zipfile
import hashlib
import numpy as np
import pandas as pd
import streamlit as st
from scipy import stats

st.title("🚀 Automated Research Pipeline")
st.caption("A guided dataset-to-evidence workflow: quality → replicate-aware analysis → figures → research outputs.")

# Prefer the dataset already loaded in Data Analyzer; otherwise accept a new file.
df = st.session_state.get("scimantra_research_df")
source_name = st.session_state.get("scimantra_research_filename", "uploaded_dataset")
if df is None:
    uploaded = st.file_uploader("Upload Excel or CSV dataset", type=["xlsx", "xls", "csv"])
    if uploaded is not None:
        source_name = uploaded.name
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
    st.info("Load a dataset in Data Analyzer first, or upload one here.")
    st.stop()

df = df.copy()
numeric = df.select_dtypes(include=np.number).columns.tolist()
categorical = [c for c in df.columns if c not in numeric]

st.success(f"Loaded **{len(df):,} rows × {len(df.columns):,} columns** from `{source_name}`")

st.subheader("1. Configure the research structure")
c1, c2, c3, c4 = st.columns(4)
group = c1.selectbox("Treatment / group", ["—"] + categorical)
replicate = c2.selectbox("Experimental unit", ["—"] + categorical)
time = c3.selectbox("Time (optional)", ["—"] + categorical)
response = c4.selectbox("Primary response", numeric if numeric else ["—"])

if response == "—":
    st.warning("Select a numeric primary response.")
    st.stop()

st.subheader("2. Quality gate")
quality = []
for col in df.columns:
    missing = int(df[col].isna().sum())
    unique = int(df[col].nunique(dropna=True))
    quality.append({"variable": col, "dtype": str(df[col].dtype), "missing": missing, "missing_%": round(100*missing/len(df), 2), "unique": unique, "constant": unique <= 1})
quality_df = pd.DataFrame(quality)
duplicate_rows = int(df.duplicated().sum())
index_like = [c for c in df.columns if str(c).lower().startswith("unnamed:")]
q1, q2, q3, q4 = st.columns(4)
q1.metric("Rows", len(df)); q2.metric("Missing cells", int(df.isna().sum().sum())); q3.metric("Duplicate rows", duplicate_rows); q4.metric("Numeric variables", len(numeric))
if duplicate_rows: st.warning(f"{duplicate_rows} duplicate rows detected. They are retained; review them before inferential analysis.")
if index_like: st.warning(f"Index-like columns detected: {', '.join(index_like[:8])}. These are excluded from automated modelling.")

st.dataframe(quality_df, width="stretch")

analysis = df.copy()
if group != "—" and replicate != "—":
    cols = [group, replicate] + ([time] if time != "—" else []) + [response]
    work = analysis[cols].copy()
    work[response] = pd.to_numeric(work[response], errors="coerce")
    work = work.dropna(subset=[group, replicate, response])
    keys = [group, replicate] + ([time] if time != "—" else [])
    unit = work.groupby(keys, dropna=False)[response].agg(n_obs="size", mean="mean", sd=lambda x: x.std(ddof=1)).reset_index()
    st.subheader("3. Replicate-aware evidence")
    st.caption("The experimental unit is treated as the independent replicate. Repeated observations are summarized rather than counted as independent rows.")
    st.dataframe(unit, width="stretch")
    valid_groups = unit[group].dropna().unique().tolist()
    arrays = [unit.loc[unit[group] == g, "mean"].dropna().to_numpy(dtype=float) for g in valid_groups]
    arrays = [a for a in arrays if len(a) >= 2]
    if len(arrays) >= 2:
        if len(arrays) == 2:
            test = stats.ttest_ind(arrays[0], arrays[1], equal_var=False)
            evidence = pd.DataFrame([{"test":"Welch t-test","statistic":test.statistic,"p_value":test.pvalue}])
        else:
            test = stats.f_oneway(*arrays)
            evidence = pd.DataFrame([{"test":"One-way ANOVA","statistic":test.statistic,"p_value":test.pvalue}])
        st.dataframe(evidence, width="stretch")
    else:
        evidence = pd.DataFrame(columns=["test","statistic","p_value"])
        st.info("At least two groups with ≥2 experimental units are needed for an inferential comparison.")
else:
    st.subheader("3. Exploratory evidence")
    clean = pd.to_numeric(analysis[response], errors="coerce").dropna()
    evidence = pd.DataFrame([{"test":"Descriptive only","statistic":clean.mean() if len(clean) else np.nan,"p_value":np.nan}])
    st.info("For inferential testing, define both treatment/group and experimental-unit identifiers.")

st.subheader("4. Primary figure")
fig_df = df.copy()
fig_df[response] = pd.to_numeric(fig_df[response], errors="coerce")
if group != "—":
    plot = fig_df.dropna(subset=[response, group])
    if not plot.empty:
        st.bar_chart(plot.groupby(group)[response].mean())
else:
    st.line_chart(fig_df[response].dropna().reset_index(drop=True))

st.subheader("5. Pipeline readiness")
checks = {
    "Dataset loaded": df is not None and not df.empty,
    "Primary response selected": response != "—",
    "Treatment/group defined": group != "—",
    "Experimental unit defined": replicate != "—",
    "At least two groups for inference": group != "—" and replicate != "—" and len(set(df[group].dropna())) >= 2,
    "No duplicate rows": duplicate_rows == 0,
}
ready_count = sum(checks.values())
for label, ok in checks.items():
    st.write(("✅" if ok else "⚠️") + " " + label)
st.progress(ready_count / len(checks), text=f"Pipeline readiness: {ready_count}/{len(checks)}")

st.subheader("6. Reproducibility manifest")
raw_bytes = df.to_csv(index=False).encode("utf-8")
fingerprint = hashlib.sha256(raw_bytes).hexdigest()
manifest = pd.DataFrame([{
    "source": source_name,
    "rows": len(df),
    "columns": len(df.columns),
    "primary_response": response,
    "group": group,
    "experimental_unit": replicate,
    "time": time,
    "duplicate_rows": duplicate_rows,
    "sha256": fingerprint,
    "analysis_rule": "One value per experimental unit; repeated observations are not independent replicates.",
}])
st.dataframe(manifest, width="stretch")

buffer = io.BytesIO()
with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("manifest.csv", manifest.to_csv(index=False))
    z.writestr("quality_audit.csv", quality_df.to_csv(index=False))
    z.writestr("evidence.csv", evidence.to_csv(index=False))
    z.writestr("dataset.csv", df.to_csv(index=False))
    z.writestr("README.txt", "SciMantra Automated Research Pipeline\n\nReview quality flags, experimental-unit definition, statistical assumptions and study design before publication.\n")
st.download_button("📦 Download automated research package", buffer.getvalue(), "scimantra_automated_research_package.zip", "application/zip")
st.info("Scientific safeguard: automation organizes and summarizes evidence; it does not automatically delete outliers, choose a favorable analysis, or certify publication readiness.")
