from __future__ import annotations

import io
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from src.scimantra.research_session import get_dataframe, metadata

st.set_page_config(page_title="H₂S Optimization & Publication", page_icon="📈", layout="wide")

st.title("📈 H₂S Optimization & Publication Evidence")
st.caption("Identify the best observed operating condition in your dataset, visualize trade-offs, and export a manuscript-ready evidence table. This is an observed-data ranking tool, not an automatic claim of global optimum.")


def num(df, col):
    return pd.to_numeric(df[col], errors="coerce")


def find(df, words):
    return [c for c in df.columns if any(w in str(c).lower().replace("₂", "2") for w in words)]


def xlsx(df):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Optimization")
    return buf.getvalue()

current_df = get_dataframe()
use_current = current_df is not None and st.checkbox("Use current Data Analyzer dataset", value=True, key="h2s_opt_use_current_dataset")
if use_current:
    meta = metadata()
    st.success(f"Current Data Analyzer dataset: **{meta['filename']}**" + (f" • worksheet: **{meta['sheet']}**" if meta.get('sheet') else ""))
    file = io.BytesIO(current_df.to_csv(index=False).encode("utf-8"))
    file.name = "current_data.csv"
else:
    file = st.file_uploader("Upload H₂S experimental dataset", type=["xlsx", "csv"])
if not file:
    st.info("Upload your experimental dataset to rank observed operating conditions.")
    st.stop()

try:
    if file.name.lower().endswith(".csv"):
        df = pd.read_csv(file)
    else:
        book = pd.ExcelFile(file)
        scores = {}
        for s in book.sheet_names:
            d = pd.read_excel(book, sheet_name=s, nrows=1000)
            scores[s] = sum(pd.to_numeric(d[c], errors="coerce").notna().sum() for c in d.columns)
        sheet = st.selectbox("Worksheet", sorted(book.sheet_names, key=lambda s: scores[s], reverse=True), format_func=lambda s: f"{s} • {scores[s]:,} numeric cells")
        df = pd.read_excel(book, sheet_name=sheet)
except Exception as exc:
    st.error(f"Could not read dataset: {exc}")
    st.stop()

if df.empty:
    st.warning("Dataset is empty.")
    st.stop()

h2s = find(df, ["h2s", "h₂s", "hydrogen sulfide", "sulfide", "sulphide"])
flow = find(df, ["flow", "gas flow", "air flow"])
volume = find(df, ["reactor volume", "bed volume", "volume"])
time = find(df, ["time", "hour", "hr", "day", "minute", "min"])
groups = find(df, ["treatment", "reactor", "condition", "group", "control"])

if not h2s:
    st.warning("No H₂S/sulfide field detected. Rename the response column to include H₂S, sulfide or sulphide.")
    st.stop()

st.markdown("### 1. Define the performance objective")
objective = st.radio("Optimization objective", ["Maximum removal efficiency", "Minimum effluent H₂S", "Maximum removal with lowest EBRT"], horizontal=True)

inlet = [c for c in h2s if any(k in str(c).lower() for k in ["inlet", "influent", "input", "initial"])]
outlet = [c for c in h2s if any(k in str(c).lower() for k in ["outlet", "effluent", "output", "final"])]

if inlet and outlet:
    a = st.selectbox("Influent H₂S", inlet)
    b = st.selectbox("Effluent H₂S", outlet)
else:
    st.info("Separate inlet and outlet fields were not both detected. Select the response fields manually.")
    a = st.selectbox("Influent / reference H₂S", h2s)
    b = st.selectbox("Effluent H₂S", [c for c in h2s if c != a] or h2s)

work = pd.DataFrame({"Influent H₂S": num(df, a), "Effluent H₂S": num(df, b)})
if time:
    tc = st.selectbox("Time / run identifier (optional)", ["None"] + time)
    if tc != "None": work["Time"] = df[tc]
else:
    tc = "None"

if groups:
    gc = st.selectbox("Operating group / treatment (optional)", ["None"] + groups)
    if gc != "None": work["Group"] = df[gc]
else:
    gc = "None"

if flow:
    fc = st.selectbox("Flow rate (optional)", ["None"] + flow)
    if fc != "None": work["Flow"] = num(df, fc)
else:
    fc = "None"
if volume:
    vc = st.selectbox("Reactor volume (optional)", ["None"] + volume)
    if vc != "None": work["Volume"] = num(df, vc)
else:
    vc = "None"

work = work.replace([np.inf, -np.inf], np.nan).dropna(subset=["Influent H₂S", "Effluent H₂S"]).copy()
work = work[work["Influent H₂S"] != 0].copy()
if work.empty:
    st.warning("No paired non-zero influent/effluent observations are available.")
    st.stop()

work["Removal %"] = (work["Influent H₂S"] - work["Effluent H₂S"]) / work["Influent H₂S"] * 100
if "Flow" in work and "Volume" in work:
    valid = (work["Flow"] > 0) & (work["Volume"] > 0)
    work.loc[valid, "EBRT"] = work.loc[valid, "Volume"] / work.loc[valid, "Flow"]
    work.loc[~valid, "EBRT"] = np.nan

st.markdown("### 2. Observed-condition ranking")
metric = "Removal %" if objective != "Minimum effluent H₂S" else "Effluent H₂S"
ascending = objective == "Minimum effluent H₂S"
if objective == "Maximum removal with lowest EBRT" and "EBRT" in work:
    valid = work.dropna(subset=["Removal %", "EBRT"]).copy()
    if len(valid):
        # Pareto frontier: higher removal and lower EBRT are both desirable.
        pareto = []
        for i, row in valid.iterrows():
            dominated = ((valid["Removal %"] >= row["Removal %"]) & (valid["EBRT"] <= row["EBRT"]) & ((valid["Removal %"] > row["Removal %"]) | (valid["EBRT"] < row["EBRT"]))).any()
            if not dominated: pareto.append(i)
        work["Pareto efficient"] = False
        work.loc[pareto, "Pareto efficient"] = True
        ranked = work.sort_values(["Pareto efficient", "Removal %", "EBRT"], ascending=[False, False, True])
    else:
        ranked = work.sort_values("Removal %", ascending=False)
else:
    ranked = work.sort_values(metric, ascending=ascending).copy()

best = ranked.iloc[0]
c = st.columns(5)
c[0].metric("Best observed removal", f"{best['Removal %']:.3f}%")
c[1].metric("Effluent H₂S", f"{best['Effluent H₂S']:.5g}")
c[2].metric("Influent H₂S", f"{best['Influent H₂S']:.5g}")
c[3].metric("Observed rows", len(work))
c[4].metric("EBRT", f"{best['EBRT']:.5g}" if "EBRT" in best and pd.notna(best.get("EBRT")) else "—")

st.success("Best observed condition identified from the uploaded observations. Verify replication, uncertainty and experimental design before calling it an optimum in a manuscript.")

st.markdown("### Ranked evidence table")
ranked = ranked.reset_index(drop=True)
ranked.insert(0, "Rank", np.arange(1, len(ranked) + 1))
st.dataframe(ranked.round(6), width="stretch", hide_index=True)

if "Group" in work:
    st.markdown("### 3. Group-level optimum")
    agg = work.groupby("Group").agg(N=("Removal %", "count"), Mean_Removal=("Removal %", "mean"), SD_Removal=("Removal %", "std"), Mean_Effluent=("Effluent H₂S", "mean")).reset_index()
    agg["SEM_Removal"] = agg["SD_Removal"] / np.sqrt(agg["N"])
    agg["CV_%"] = agg["SD_Removal"] / agg["Mean_Removal"].replace(0, np.nan) * 100
    agg = agg.sort_values("Mean_Removal", ascending=False).reset_index(drop=True)
    agg.insert(0, "Rank", np.arange(1, len(agg) + 1))
    st.dataframe(agg.round(6), width="stretch", hide_index=True)
    st.plotly_chart(px.bar(agg, x="Group", y="Mean_Removal", error_y="SEM_Removal", title="Mean H₂S removal by group"), width="stretch")

st.markdown("### 4. Publication figures")
left, right = st.columns(2)
with left:
    st.plotly_chart(px.scatter(work, x="Influent H₂S", y="Effluent H₂S", title="Influent vs effluent H₂S", hover_data=["Removal %"]), width="stretch")
with right:
    if "EBRT" in work and work["EBRT"].notna().any():
        st.plotly_chart(px.scatter(work, x="EBRT", y="Removal %", title="Removal efficiency vs EBRT", hover_data=["Effluent H₂S"]), width="stretch")
    else:
        st.plotly_chart(px.histogram(work, x="Removal %", nbins=15, title="Distribution of H₂S removal efficiency"), width="stretch")

if "Group" in work:
    st.plotly_chart(px.box(work, x="Group", y="Removal %", points="all", title="Observed removal efficiency by group"), width="stretch")

st.markdown("### 5. Manuscript-ready wording")
if "Group" in work:
    best_group = agg.iloc[0]["Group"] if len(agg) else "the leading group"
    sentence = f"Across the analyzed observations, {best_group} showed the highest mean H₂S removal ({agg.iloc[0]['Mean_Removal']:.2f}% ± {agg.iloc[0]['SEM_Removal']:.2f} SEM; n={int(agg.iloc[0]['N'])}). The highest single observed removal was {work['Removal %'].max():.2f}%."
else:
    sentence = f"Across the analyzed observations, the highest single observed H₂S removal was {work['Removal %'].max():.2f}%, while the lowest observed effluent concentration was {work['Effluent H₂S'].min():.5g}."
st.text_area("Draft result sentence", sentence, height=100)
st.caption("Edit this text to reflect your study design, units, uncertainty, statistical model and replicate definition. Avoid presenting an observed maximum as a validated process optimum without confirmation experiments.")

st.markdown("### 6. Export")
st.download_button("⬇️ Download ranked optimization workbook", xlsx(ranked), "scimantra_h2s_optimization.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", width="stretch")
st.download_button("⬇️ Download ranked CSV", ranked.to_csv(index=False).encode(), "scimantra_h2s_optimization.csv", "text/csv", width="stretch")
