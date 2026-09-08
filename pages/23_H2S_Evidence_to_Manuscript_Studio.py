from __future__ import annotations

import io
import re
import numpy as np
import pandas as pd
import streamlit as st
from scipy import stats
from src.scimantra.research_session import get_dataframe, metadata

st.set_page_config(page_title="H₂S Evidence-to-Manuscript Studio", page_icon="📝", layout="wide")

st.title("📝 H₂S Evidence-to-Manuscript Studio")
st.caption("Turn analyzed H₂S observations into traceable Results, Methods, figure captions and an evidence package. Text is generated only from the selected dataset and reported statistics; it does not invent findings.")


def num(df, col):
    return pd.to_numeric(df[col], errors="coerce")


def find(df, words):
    return [c for c in df.columns if any(w in str(c).lower().replace("₂", "2") for w in words)]


def excel_bytes(tables):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        for name, table in tables.items():
            table.to_excel(writer, index=False, sheet_name=name[:31])
    return buf.getvalue()


df = get_dataframe()
if df is None:
    file = st.file_uploader("Upload H₂S dataset", type=["xlsx", "csv"])
    if not file:
        st.info("Open Data Analyzer first and select your H₂S worksheet, or upload a dataset here.")
        st.stop()
    if file.name.lower().endswith(".csv"):
        df = pd.read_csv(file)
        source = file.name
    else:
        book = pd.ExcelFile(file)
        sheet = st.selectbox("Worksheet", book.sheet_names)
        df = pd.read_excel(book, sheet_name=sheet)
        source = f"{file.name} • {sheet}"
else:
    meta = metadata()
    source = meta.get("filename", "current dataset")
    if meta.get("sheet"):
        source += f" • {meta['sheet']}"
    st.success(f"Using current Data Analyzer dataset: **{source}**")

h2s = find(df, ["h2s", "hydrogen sulfide", "sulfide", "sulphide"])
inlet = [c for c in h2s if any(k in str(c).lower() for k in ["inlet", "influent", "input", "initial"])]
outlet = [c for c in h2s if any(k in str(c).lower() for k in ["outlet", "effluent", "output", "final"])]
groups = find(df, ["treatment", "reactor", "condition", "group"])
replicates = find(df, ["replicate", "rep", "biological replicate", "technical replicate"])
time_cols = find(df, ["time", "hour", "hr", "day", "minute", "min"])
ebrt_cols = find(df, ["ebrt"])
load_cols = find(df, ["inlet h2s load", "h2s loading", "loading"])
ph_cols = find(df, ["ph"])

if not h2s:
    st.warning("No H₂S-like columns detected.")
    st.stop()

st.markdown("### 1. Define the experimental structure")
a = st.selectbox("Inlet / influent H₂S", inlet or h2s)
b = st.selectbox("Outlet / effluent H₂S", outlet or [c for c in h2s if c != a] or h2s)
group = st.selectbox("Experimental group / treatment", ["None"] + groups)
rep = st.selectbox("Experimental unit / replicate ID", ["None"] + replicates)
time_col = st.selectbox("Time / run variable", ["None"] + time_cols)

work = pd.DataFrame({"Inlet H₂S": num(df, a), "Outlet H₂S": num(df, b)})
if group != "None": work["Group"] = df[group]
if rep != "None": work["Replicate"] = df[rep]
if time_col != "None": work["Time"] = df[time_col]
for label, cols in [("EBRT", ebrt_cols), ("Loading", load_cols), ("pH", ph_cols)]:
    if cols:
        chosen = st.selectbox(f"{label} variable (optional)", ["None"] + cols, key=f"studio_{label}")
        if chosen != "None": work[label] = num(df, chosen).reindex(work.index)

work = work.replace([np.inf, -np.inf], np.nan).dropna(subset=["Inlet H₂S", "Outlet H₂S"]).copy()
work = work[work["Inlet H₂S"] != 0]
work["Removal %"] = (work["Inlet H₂S"] - work["Outlet H₂S"]) / work["Inlet H₂S"] * 100

if work.empty:
    st.warning("No valid paired inlet/outlet observations remain.")
    st.stop()

# Experimental-unit aggregation prevents accidental treatment of repeated technical measurements as independent observations.
analysis = work.copy()
aggregation_note = "Each valid inlet/outlet row is treated as one observation."
if "Replicate" in work:
    keys = [c for c in ["Group", "Replicate", "Time"] if c in work]
    if keys:
        numeric_cols = [c for c in ["Inlet H₂S", "Outlet H₂S", "Removal %", "EBRT", "Loading", "pH"] if c in work]
        analysis = work.groupby(keys, dropna=False)[numeric_cols].mean().reset_index()
        aggregation_note = "Repeated rows were averaged within each selected experimental-unit/replicate key before group-level inference."

st.markdown("### 2. Evidence quality gate")
qc = []
qc.append({"Check": "Paired inlet/outlet observations", "Value": len(work), "Status": "PASS" if len(work) >= 3 else "WARN"})
if "Group" in analysis:
    counts = analysis.groupby("Group").size()
    qc.append({"Check": "Experimental groups", "Value": len(counts), "Status": "PASS" if len(counts) >= 2 else "WARN"})
    qc.append({"Check": "Minimum observations per group", "Value": int(counts.min()), "Status": "PASS" if counts.min() >= 3 else "WARN"})
if "Replicate" in work:
    qc.append({"Check": "Replicate identifiers detected", "Value": work["Replicate"].nunique(dropna=True), "Status": "PASS" if work["Replicate"].nunique(dropna=True) >= 2 else "WARN"})
qc.append({"Check": "Negative removal values", "Value": int((work["Removal %"] < 0).sum()), "Status": "INFO" if (work["Removal %"] < 0).any() else "PASS"})
qc_df = pd.DataFrame(qc)
st.dataframe(qc_df, width="stretch", hide_index=True)
st.caption(aggregation_note)

mean_r = analysis["Removal %"].mean()
sd_r = analysis["Removal %"].std(ddof=1) if len(analysis) > 1 else np.nan
sem_r = sd_r / np.sqrt(len(analysis)) if len(analysis) > 1 else np.nan
ci = stats.t.ppf(.975, len(analysis)-1) * sem_r if len(analysis) > 1 else np.nan
c = st.columns(5)
c[0].metric("Analysis units", len(analysis))
c[1].metric("Mean removal", f"{mean_r:.2f}%")
c[2].metric("SD", f"{sd_r:.2f}" if pd.notna(sd_r) else "—")
c[3].metric("SEM", f"{sem_r:.2f}" if pd.notna(sem_r) else "—")
c[4].metric("95% CI", f"{mean_r-ci:.2f}–{mean_r+ci:.2f}%" if pd.notna(ci) else "—")

st.markdown("### 3. Statistical evidence")
tables = {"Analysis_Data": analysis.copy(), "Quality_Gate": qc_df.copy()}
if "Group" in analysis:
    grouped = analysis.groupby("Group")["Removal %"]
    summary = grouped.agg(N="count", Mean="mean", SD="std").reset_index()
    summary["SEM"] = summary["SD"] / np.sqrt(summary["N"])
    summary["95% CI low"] = summary.apply(lambda r: r.Mean - stats.t.ppf(.975, r.N-1)*r.SEM if r.N > 1 else np.nan, axis=1)
    summary["95% CI high"] = summary.apply(lambda r: r.Mean + stats.t.ppf(.975, r.N-1)*r.SEM if r.N > 1 else np.nan, axis=1)
    st.dataframe(summary.round(5), width="stretch", hide_index=True)
    tables["Group_Summary"] = summary
    keys = list(grouped.groups.keys())
    if len(keys) == 2:
        vals = [grouped.get_group(k).dropna().to_numpy() for k in keys]
        welch = stats.ttest_ind(vals[0], vals[1], equal_var=False)
        mw = stats.mannwhitneyu(vals[0], vals[1], alternative="two-sided")
        test = pd.DataFrame([{"Test":"Welch t-test","Statistic":welch.statistic,"p-value":welch.pvalue},{"Test":"Mann–Whitney U","Statistic":mw.statistic,"p-value":mw.pvalue}])
    elif len(keys) >= 3:
        vals = [grouped.get_group(k).dropna().to_numpy() for k in keys]
        an = stats.f_oneway(*vals)
        kr = stats.kruskal(*vals)
        test = pd.DataFrame([{"Test":"One-way ANOVA","Statistic":an.statistic,"p-value":an.pvalue},{"Test":"Kruskal–Wallis","Statistic":kr.statistic,"p-value":kr.pvalue}])
    else:
        test = pd.DataFrame(columns=["Test","Statistic","p-value"])
    if not test.empty:
        st.dataframe(test.round(6), width="stretch", hide_index=True)
        tables["Statistical_Tests"] = test

st.markdown("### 4. Traceable manuscript text")
top_group = None
if "Group" in analysis:
    gsum = analysis.groupby("Group")["Removal %"].agg(["count", "mean", "std"]).sort_values("mean", ascending=False)
    if len(gsum): top_group = gsum.index[0]

results_sentence = f"Across {len(analysis)} analysis units, mean H₂S removal efficiency was {mean_r:.2f}% ± {sem_r:.2f} SEM" if pd.notna(sem_r) else f"Across {len(analysis)} analysis units, mean H₂S removal efficiency was {mean_r:.2f}%"
results_sentence += "."
if top_group is not None:
    results_sentence += f" The highest group mean was observed for {top_group} ({gsum.loc[top_group, 'mean']:.2f}% ± {(gsum.loc[top_group, 'std']/np.sqrt(gsum.loc[top_group, 'count'])):.2f} SEM; n={int(gsum.loc[top_group, 'count'])})."

methods_sentence = (f"H₂S removal efficiency was calculated from paired inlet and outlet concentrations as ((inlet − outlet) / inlet) × 100. "
                    f"The dataset source was {source}. {aggregation_note} "
                    f"Statistical screening used replicate-level summaries where an experimental-unit/replicate identifier was supplied.")

caption = "Figure. H₂S removal efficiency across the analyzed experimental conditions. Values represent the selected analysis units; error bars, where shown, should be defined explicitly in the final figure legend."

st.text_area("Results draft", results_sentence, height=110)
st.text_area("Methods draft", methods_sentence, height=130)
st.text_area("Figure caption draft", caption, height=100)

st.markdown("### 5. Decision log")
decisions = pd.DataFrame([
    {"Decision": "Response calculation", "Choice": "Removal efficiency from paired inlet/outlet H₂S"},
    {"Decision": "Experimental unit", "Choice": "Replicate-level aggregation when Replicate ID is supplied; otherwise row-level screening"},
    {"Decision": "Primary summary", "Choice": "Mean ± SEM with 95% CI"},
    {"Decision": "Inferential screening", "Choice": "Welch/Mann–Whitney for 2 groups; ANOVA/Kruskal–Wallis for ≥3 groups"},
    {"Decision": "Interpretation", "Choice": "Association/screening only; no automatic causal or global-optimum claim"},
])
st.dataframe(decisions, width="stretch", hide_index=True)
tables["Decision_Log"] = decisions

st.markdown("### 6. Evidence package")
package = excel_bytes(tables)
st.download_button("⬇️ Download complete H₂S evidence package", package, "scimantra_h2s_evidence_to_manuscript.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", width="stretch")
text = "H₂S EVIDENCE-TO-MANUSCRIPT STUDIO\n\nSOURCE\n" + source + "\n\nRESULTS\n" + results_sentence + "\n\nMETHODS\n" + methods_sentence + "\n\nFIGURE CAPTION\n" + caption + "\n\nDECISION LOG\n" + decisions.to_string(index=False)
st.download_button("⬇️ Download manuscript text", text.encode("utf-8"), "scimantra_h2s_manuscript_draft.txt", "text/plain", width="stretch")
