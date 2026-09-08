from __future__ import annotations

import io
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from src.scimantra.research_session import get_dataframe, metadata
from scipy import stats

st.set_page_config(page_title="H₂S Bioreactor Research Suite", page_icon="🧪", layout="wide")

st.title("🧪 H₂S Bioreactor Research Suite")
st.caption("Research-oriented screening for H₂S removal, reactor performance, operating conditions, replicates and publication-ready evidence.")


def num(df, col):
    return pd.to_numeric(df[col], errors="coerce")


def find_cols(df, words):
    return [c for c in df.columns if any(w in str(c).lower().replace("₂", "2") for w in words)]


def excel_bytes(df):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="H2S_Analysis")
    return buf.getvalue()

current_df = get_dataframe()
use_current = current_df is not None and st.checkbox("Use current Data Analyzer dataset", value=True, key="h2s_use_current_dataset")
if use_current:
    meta = metadata()
    st.success(f"Current Data Analyzer dataset: **{meta['filename']}**" + (f" • worksheet: **{meta['sheet']}**" if meta.get('sheet') else ""))
    uploaded = io.BytesIO(current_df.to_csv(index=False).encode("utf-8"))
    uploaded.name = "current_data.csv"
else:
    uploaded = st.file_uploader("Upload H₂S / reactor dataset", type=["xlsx", "csv"], help="Use a workbook containing experimental observations. Original data are not changed.")
if not uploaded:
    st.info("Upload your H₂S experimental workbook to begin.")
    st.markdown("### Recommended columns")
    st.write("Time • H₂S inlet/effluent • Treatment/Reactor • Replicate • pH • Flow • Reactor volume • EBRT • Loading")
    st.stop()

try:
    if uploaded.name.lower().endswith(".csv"):
        df = pd.read_csv(uploaded)
        sheet = None
    else:
        book = pd.ExcelFile(uploaded)
        scores = {}
        for s in book.sheet_names:
            d = pd.read_excel(book, sheet_name=s, nrows=1000)
            numeric_count = sum(pd.to_numeric(d[c], errors="coerce").notna().sum() for c in d.columns)
            scores[s] = (numeric_count, len(d.columns), len(d))
        ranked = sorted(book.sheet_names, key=lambda s: scores[s], reverse=True)
        sheet = st.selectbox("Excel worksheet", ranked, format_func=lambda s: f"{s} • {scores[s][0]:,} numeric cells")
        df = pd.read_excel(book, sheet_name=sheet)
except Exception as exc:
    st.error(f"Could not read the dataset: {exc}")
    st.stop()

if df.empty:
    st.warning("The selected dataset is empty.")
    st.stop()

numeric = [c for c in df.columns if pd.to_numeric(df[c], errors="coerce").notna().sum() >= max(1, int(df[c].notna().sum() * 0.8))]
categorical = [c for c in df.columns if c not in numeric]
h2s = find_cols(df, ["h2s", "h₂s", "hydrogen sulfide", "sulfide", "sulphide"])
time_cols = find_cols(df, ["time", "hour", "hr", "day", "minute", "min"])
ph = find_cols(df, ["ph"])
flow = find_cols(df, ["flow", "gas flow", "air flow"])
volume = find_cols(df, ["reactor volume", "bed volume", "volume"])
replicate = find_cols(df, ["replicate", "rep", "biological replicate", "technical replicate"])
treatment = [c for c in categorical if any(k in str(c).lower() for k in ["treatment", "reactor", "condition", "group", "control"])]

m = st.columns(6)
m[0].metric("Rows", f"{len(df):,}")
m[1].metric("Columns", f"{len(df.columns):,}")
m[2].metric("H₂S fields", f"{len(h2s):,}")
m[3].metric("Time fields", f"{len(time_cols):,}")
m[4].metric("pH fields", f"{len(ph):,}")
m[5].metric("Replicate fields", f"{len(replicate):,}")

if not h2s:
    st.warning("No H₂S/sulfide column was detected. Rename the concentration column to include H₂S, sulfide or sulphide.")
    st.stop()

st.markdown("### 🔬 Analysis workspace")
mode = st.selectbox("Choose analysis", [
    "H₂S removal performance",
    "Replicate-aware performance",
    "H₂S time-course",
    "Operating-condition relationships",
    "EBRT & loading optimization",
    "Treatment comparison",
    "Research summary & export",
])

if mode == "H₂S removal performance":
    inlet = [c for c in h2s if any(k in str(c).lower() for k in ["inlet", "influent", "input", "initial"])]
    outlet = [c for c in h2s if any(k in str(c).lower() for k in ["outlet", "effluent", "output", "final"])]
    a = st.selectbox("Influent / inlet H₂S", inlet or h2s)
    b = st.selectbox("Effluent / outlet H₂S", outlet or [c for c in h2s if c != a] or h2s)
    if a == b:
        st.info("Select separate inlet and outlet H₂S columns.")
    else:
        work = pd.DataFrame({"Influent H₂S": num(df, a), "Effluent H₂S": num(df, b)}).replace([np.inf, -np.inf], np.nan).dropna()
        work = work[work["Influent H₂S"] != 0].copy()
        work["Removal %"] = (work["Influent H₂S"] - work["Effluent H₂S"]) / work["Influent H₂S"] * 100
        c = st.columns(4)
        c[0].metric("Mean influent", f"{work['Influent H₂S'].mean():.5g}")
        c[1].metric("Mean effluent", f"{work['Effluent H₂S'].mean():.5g}")
        c[2].metric("Mean removal", f"{work['Removal %'].mean():.5g}%")
        c[3].metric("Observations", len(work))
        st.plotly_chart(px.box(work, y="Removal %", points="all", title="H₂S removal efficiency"), width="stretch")
        st.dataframe(work.round(6), width="stretch", hide_index=True)
        st.download_button("⬇️ Download removal results", work.to_csv(index=False).encode(), "h2s_removal_results.csv", "text/csv", width="stretch")

elif mode == "Replicate-aware performance":
    group_candidates = treatment + categorical
    rep = st.selectbox("Replicate identifier", replicate or ["(No replicate column)"])
    group = st.selectbox("Experimental group", group_candidates or ["(No group column)"])
    response = st.selectbox("H₂S response", h2s)
    if rep == "(No replicate column)":
        st.info("Add a Replicate column for explicit biological/technical replicate tracking. Group-level statistics below remain available.")
    work = pd.DataFrame({"Group": df[group], "Response": num(df, response)})
    if rep != "(No replicate column)":
        work["Replicate"] = df[rep]
    work = work.dropna(subset=["Group", "Response"])
    grouped = work.groupby("Group")["Response"]
    result = grouped.agg(N="count", Mean="mean", SD="std", Median="median", Min="min", Max="max").reset_index()
    result["SEM"] = result["SD"] / np.sqrt(result["N"])
    result["CV %"] = np.where(result["Mean"] != 0, result["SD"] / result["Mean"] * 100, np.nan)
    st.dataframe(result.round(6), width="stretch", hide_index=True)
    st.plotly_chart(px.box(work, x="Group", y="Response", points="all", title=f"{response} — replicate distribution"), width="stretch")
    if rep != "(No replicate column)":
        counts = work.groupby(["Group", "Replicate"]).size().reset_index(name="Observations")
        st.markdown("#### Replicate structure")
        st.dataframe(counts, width="stretch", hide_index=True)
    st.caption("Do not treat technical replicates as independent biological replicates without an appropriate experimental model.")

elif mode == "H₂S time-course":
    y = st.selectbox("H₂S response", h2s)
    x = st.selectbox("Time / sequence", time_cols or numeric)
    group = st.selectbox("Optional group", ["None"] + treatment + categorical)
    cols = [x, y] if group == "None" else [x, y, group]
    work = df[cols].copy(); work[y] = num(work, y); work = work.dropna()
    fig = px.line(work, x=x, y=y, color=None if group == "None" else group, markers=True, title=f"{y} across {x}")
    st.plotly_chart(fig, width="stretch")
    if group != "None":
        summary = work.groupby([group, x], as_index=False)[y].agg(Mean="mean", SD="std", N="count")
        summary["SEM"] = summary["SD"] / np.sqrt(summary["N"])
        st.dataframe(summary.round(6), width="stretch", hide_index=True)
    st.download_button("⬇️ Download time-course", work.to_csv(index=False).encode(), "h2s_timecourse.csv", "text/csv", width="stretch")

elif mode == "Operating-condition relationships":
    y = st.selectbox("H₂S response", h2s)
    candidates = ph + [c for c in numeric if c not in h2s and c not in time_cols]
    if not candidates:
        st.info("No additional operating variable was detected.")
    else:
        x = st.selectbox("Operating variable", list(dict.fromkeys(candidates)))
        work = pd.DataFrame({x: num(df, x), y: num(df, y)}).dropna()
        if len(work) >= 3 and work[x].nunique() > 1:
            r = stats.linregress(work[x], work[y])
            c = st.columns(5)
            c[0].metric("N", len(work)); c[1].metric("Slope", f"{r.slope:.5g}"); c[2].metric("Intercept", f"{r.intercept:.5g}"); c[3].metric("R²", f"{r.rvalue**2:.5g}"); c[4].metric("p-value", f"{r.pvalue:.5g}")
            st.plotly_chart(px.scatter(work, x=x, y=y, trendline="ols", title=f"{y} vs {x}"), width="stretch")
        else:
            st.info("At least three paired observations and variation in the operating variable are needed.")

elif mode == "EBRT & loading optimization":
    h = st.selectbox("H₂S concentration", h2s)
    f = st.selectbox("Flow rate", flow or numeric)
    v = st.selectbox("Reactor volume", volume or numeric)
    work = pd.DataFrame({"H₂S": num(df, h), "Flow": num(df, f), "Volume": num(df, v)}).replace([np.inf, -np.inf], np.nan).dropna()
    work = work[(work["Flow"] > 0) & (work["Volume"] > 0)]
    if len(work):
        work["EBRT"] = work["Volume"] / work["Flow"]
        work["Loading"] = work["H₂S"] * work["Flow"]
        c = st.columns(4); c[0].metric("N", len(work)); c[1].metric("Mean EBRT", f"{work['EBRT'].mean():.5g}"); c[2].metric("Mean loading", f"{work['Loading'].mean():.5g}"); c[3].metric("Max H₂S", f"{work['H₂S'].max():.5g}")
        st.plotly_chart(px.scatter(work, x="EBRT", y="H₂S", trendline="ols", title="H₂S vs EBRT"), width="stretch")
        st.plotly_chart(px.scatter(work, x="Loading", y="H₂S", trendline="ols", title="H₂S vs loading"), width="stretch")
        st.dataframe(work.round(6), width="stretch", hide_index=True)
        st.download_button("⬇️ Download EBRT/loading analysis", excel_bytes(work), "h2s_ebrt_loading.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", width="stretch")
        st.caption("Loading is calculated as concentration × flow. Confirm your mass basis, flow basis and standard/actual conditions before using values in a manuscript.")
    else:
        st.info("No valid positive flow/volume observations were available.")

elif mode == "Treatment comparison":
    if not treatment:
        st.info("No obvious treatment/group column was detected. Add a column such as Treatment, Reactor, Condition, Group or Control.")
    else:
        group = st.selectbox("Treatment/group", treatment)
        response = st.selectbox("Response", h2s)
        work = pd.DataFrame({group: df[group], response: num(df, response)}).dropna()
        groups = [g[response].to_numpy() for _, g in work.groupby(group)]
        result = work.groupby(group)[response].agg(N="count", Mean="mean", SD="std").reset_index(); result["SEM"] = result["SD"] / np.sqrt(result["N"]); result["CV %"] = result["SD"] / result["Mean"] * 100
        st.dataframe(result.round(6), width="stretch", hide_index=True)
        st.plotly_chart(px.box(work, x=group, y=response, points="all", title=f"{response} by {group}"), width="stretch")
        if len(groups) == 2:
            r = stats.ttest_ind(*groups, equal_var=False); st.info(f"Welch t-test screening: t = {r.statistic:.5g}, p = {r.pvalue:.5g}")
        elif len(groups) >= 3:
            r = stats.f_oneway(*groups); st.info(f"One-way ANOVA screening: F = {r.statistic:.5g}, p = {r.pvalue:.5g}")
        st.caption("These are screening analyses. Match the final model to biological replication, repeated measures, blocking and your preregistered/defined analysis plan.")

else:
    st.markdown("### 📋 Research summary")
    st.write(f"**Dataset:** {uploaded.name}")
    st.write(f"**Observations:** {len(df):,} rows × {len(df.columns):,} columns")
    st.write(f"**Detected H₂S fields:** {', '.join(map(str, h2s))}")
    st.write(f"**Detected time fields:** {', '.join(map(str, time_cols)) or 'None'}")
    st.write(f"**Detected pH fields:** {', '.join(map(str, ph)) or 'None'}")
    st.write(f"**Detected replicate fields:** {', '.join(map(str, replicate)) or 'None'}")
    st.write(f"**Missing cells:** {int(df.isna().sum().sum()):,} • **Duplicate rows:** {int(df.duplicated().sum()):,}")
    summary = pd.DataFrame({"Column": df.columns, "Type": [str(df[c].dtype) for c in df.columns], "Missing": [int(df[c].isna().sum()) for c in df.columns], "Unique": [int(df[c].nunique(dropna=True)) for c in df.columns]})
    st.dataframe(summary, width="stretch", hide_index=True)
    st.download_button("⬇️ Download analysis-ready workbook", excel_bytes(df), "scimantra_h2s_analysis_ready.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", width="stretch")
    st.warning("Research note: automated detection is a convenience layer, not a substitute for checking units, calibration, experimental design, replicate definitions and statistical assumptions.")
