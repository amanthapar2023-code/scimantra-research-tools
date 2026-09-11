import numpy as np
import pandas as pd
import streamlit as st
from scipy import stats

st.title("🧪 Research Data Quality Audit")
st.caption("A transparent pre-analysis audit for missingness, duplicates, replicate balance, distributions and potential outliers.")

df = st.session_state.get("scimantra_research_df")
if df is None:
    up = st.file_uploader("Upload Excel or CSV dataset", type=["xlsx", "xls", "csv"])
    if up is not None:
        try:
            df = pd.read_csv(up) if up.name.lower().endswith(".csv") else pd.read_excel(up)
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

st.subheader("1. Dataset integrity")
missing = int(df.isna().sum().sum())
duplicates = int(df.duplicated().sum())
constant = [c for c in df.columns if df[c].nunique(dropna=True) <= 1]
unnamed = [c for c in df.columns if str(c).lower().startswith("unnamed:")]
metrics = st.columns(5)
metrics[0].metric("Rows", f"{len(df):,}")
metrics[1].metric("Columns", f"{len(df.columns):,}")
metrics[2].metric("Missing cells", f"{missing:,}")
metrics[3].metric("Duplicate rows", f"{duplicates:,}")
metrics[4].metric("Numeric fields", f"{len(numeric):,}")

issues = []
if missing: issues.append(f"{missing:,} missing cells detected.")
if duplicates: issues.append(f"{duplicates:,} exact duplicate rows detected; inspect before inferential analysis.")
if constant: issues.append(f"{len(constant)} constant field(s) contain no analytical variation.")
if unnamed: issues.append(f"{len(unnamed)} Unnamed/index-like field(s) detected; these are usually not analytical variables.")
if issues:
    for x in issues: st.warning(x)
else: st.success("No basic integrity flags detected.")

st.subheader("2. Field-level quality")
field = pd.DataFrame({"field":df.columns,"dtype":[str(df[c].dtype) for c in df.columns],"n_nonmissing":[int(df[c].notna().sum()) for c in df.columns],"missing":[int(df[c].isna().sum()) for c in df.columns],"missing_%":[float(df[c].isna().mean()*100) for c in df.columns],"unique":[int(df[c].nunique(dropna=True)) for c in df.columns]})
st.dataframe(field, width="stretch")

st.subheader("3. Replicate structure audit")
if categorical:
    group = st.selectbox("Treatment / group (optional)", ["—"] + categorical)
    replicate = st.selectbox("Experimental unit / replicate (optional)", ["—"] + categorical)
    if group != "—" and replicate != "—":
        tmp = df[[group, replicate]].dropna()
        counts = tmp.groupby(group)[replicate].nunique().reset_index(name="unique_units")
        obs = tmp.groupby([group, replicate]).size().reset_index(name="observations")
        counts["min_observations_per_unit"] = obs.groupby(group)["observations"].min().reindex(counts[group]).to_numpy()
        counts["max_observations_per_unit"] = obs.groupby(group)["observations"].max().reindex(counts[group]).to_numpy()
        st.dataframe(counts, width="stretch")
        if len(counts) >= 2 and counts["unique_units"].nunique() > 1:
            st.warning("Unequal numbers of experimental units across groups are present. Report the actual n and consider the design when choosing inferential methods.")
else:
    st.info("No categorical fields are available for a replicate audit.")

st.subheader("4. Numeric distribution and outlier screening")
if numeric:
    response = st.selectbox("Numeric variable", numeric)
    method = st.selectbox("Screening method", ["IQR rule", "Robust z-score (MAD)", "Both"])
    x = pd.to_numeric(df[response], errors="coerce").dropna()
    if len(x) < 4:
        st.warning("At least 4 non-missing observations are recommended for screening.")
    else:
        q1,q3 = x.quantile([0.25,0.75]); iqr=q3-q1
        lo,hi=q1-1.5*iqr,q3+1.5*iqr
        iqr_flag=(x<lo)|(x>hi)
        med=float(x.median()); mad=float(np.median(np.abs(x-med)))
        rz=np.abs(0.6745*(x-med)/mad) if mad>0 else pd.Series(0.0,index=x.index)
        rz_flag=rz>3.5
        if method in ("IQR rule","Both"):
            st.write(f"IQR fences: **{lo:.6g} to {hi:.6g}**")
        if method in ("Robust z-score (MAD)","Both"):
            st.write(f"MAD: **{mad:.6g}**; robust |z| threshold: **3.5**")
        flags = iqr_flag if method=="IQR rule" else rz_flag if method=="Robust z-score (MAD)" else (iqr_flag|rz_flag)
        flagged = pd.DataFrame({"row_index":x.index,"value":x.to_numpy(),"IQR_flag":iqr_flag.to_numpy(),"robust_z":rz.to_numpy(),"robust_z_flag":rz_flag.to_numpy(),"flagged":flags.to_numpy()})
        st.metric("Flagged observations", f"{int(flags.sum())} / {len(x)}")
        st.dataframe(flagged[flagged["flagged"]], width="stretch")
        st.info("Outlier flags are screening signals, not automatic exclusion criteria. Investigate instrument/QC records, transcription, biological plausibility and predefined study rules before removing observations.")

st.subheader("5. Distribution diagnostics")
if numeric and len(x) >= 3:
    sh = stats.shapiro(x.sample(min(len(x),5000), random_state=0)) if len(x)>5000 else stats.shapiro(x)
    c=st.columns(3); c[0].metric("Mean",f"{x.mean():.6g}"); c[1].metric("SD",f"{x.std(ddof=1):.6g}" if len(x)>1 else "NA"); c[2].metric("Shapiro p",f"{sh.pvalue:.5g}")
    st.caption("Normality tests should be interpreted alongside plots, sample size and study design; a p-value alone does not establish normality.")

st.subheader("6. Audit report")
report = pd.DataFrame({"item":["Rows","Columns","Missing cells","Duplicate rows","Constant fields","Index-like fields","Numeric fields"],"value":[len(df),len(df.columns),missing,duplicates,len(constant),len(unnamed),len(numeric)]})
st.dataframe(report, width="stretch")
st.download_button("⬇️ Download audit report", report.to_csv(index=False).encode("utf-8"), "scimantra_data_quality_audit.csv", "text/csv")
st.info("Scientific safeguard: this audit identifies quality signals; it does not automatically delete, impute or exclude observations and does not certify publication readiness.")
