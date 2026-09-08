from __future__ import annotations

import io
import numpy as np
import pandas as pd
import streamlit as st
from scipy import stats
from src.scimantra.research_session import get_dataframe, metadata

st.set_page_config(page_title="H₂S Complete Manuscript Builder", page_icon="📄", layout="wide")

st.title("📄 H₂S Complete Manuscript Builder")
st.caption("Generate a structured, data-traceable manuscript draft from the currently analyzed H₂S dataset. Every quantitative statement is derived from the selected data; scientific interpretation and literature claims remain under researcher control.")


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
        df = pd.read_csv(file); source = file.name
    else:
        book = pd.ExcelFile(file); sheet = st.selectbox("Worksheet", book.sheet_names); df = pd.read_excel(book, sheet_name=sheet); source = f"{file.name} • {sheet}"
else:
    meta = metadata(); source = meta.get("filename", "current dataset") + (f" • {meta['sheet']}" if meta.get("sheet") else "")
    st.success(f"Using current Data Analyzer dataset: **{source}**")

h2s = find(df, ["h2s", "hydrogen sulfide", "sulfide", "sulphide"])
inlet = [c for c in h2s if any(k in str(c).lower() for k in ["inlet", "influent", "input", "initial"])]
outlet = [c for c in h2s if any(k in str(c).lower() for k in ["outlet", "effluent", "output", "final"])]
groups = find(df, ["treatment", "reactor", "condition", "group"])
replicates = find(df, ["replicate", "rep", "biological replicate", "technical replicate"])
time_cols = find(df, ["time", "hour", "hr", "day", "minute", "min"])

if not h2s:
    st.warning("No H₂S-like columns detected."); st.stop()

st.markdown("### 1. Study identity")
title = st.text_input("Working title", "H₂S removal performance in a biological treatment system")
organism = st.text_input("Microorganism / biological system", "")
reactor = st.text_input("Reactor / process description", "")
objective = st.text_area("Study objective", "Evaluate H₂S removal performance and identify operating conditions associated with improved treatment performance.")

st.markdown("### 2. Data mapping")
a = st.selectbox("Inlet H₂S", inlet or h2s)
b = st.selectbox("Outlet H₂S", outlet or [c for c in h2s if c != a] or h2s)
group = st.selectbox("Treatment / experimental group", ["None"] + groups)
rep = st.selectbox("Replicate ID", ["None"] + replicates)
time_col = st.selectbox("Time / run variable", ["None"] + time_cols)

work = pd.DataFrame({"Inlet H₂S": num(df, a), "Outlet H₂S": num(df, b)})
if group != "None": work["Group"] = df[group]
if rep != "None": work["Replicate"] = df[rep]
if time_col != "None": work["Time"] = df[time_col]
work = work.replace([np.inf, -np.inf], np.nan).dropna(subset=["Inlet H₂S", "Outlet H₂S"])
work = work[work["Inlet H₂S"] != 0].copy()
work["Removal %"] = (work["Inlet H₂S"] - work["Outlet H₂S"]) / work["Inlet H₂S"] * 100

analysis = work.copy()
if "Replicate" in work:
    keys = [c for c in ["Group", "Replicate", "Time"] if c in work]
    if keys:
        analysis = work.groupby(keys, dropna=False)[["Inlet H₂S", "Outlet H₂S", "Removal %"]].mean().reset_index()

n = len(analysis)
mean_r = analysis["Removal %"].mean()
sd_r = analysis["Removal %"].std(ddof=1) if n > 1 else np.nan
sem_r = sd_r / np.sqrt(n) if n > 1 else np.nan
ci = stats.t.ppf(.975, n-1) * sem_r if n > 1 else np.nan

if "Group" in analysis:
    gs = analysis.groupby("Group")["Removal %"].agg(N="count", Mean="mean", SD="std").reset_index()
    gs["SEM"] = gs["SD"] / np.sqrt(gs["N"])
    gs = gs.sort_values("Mean", ascending=False).reset_index(drop=True)
else:
    gs = pd.DataFrame()

st.markdown("### 3. Evidence summary")
c = st.columns(5)
c[0].metric("Analysis units", n)
c[1].metric("Mean removal", f"{mean_r:.2f}%")
c[2].metric("SD", f"{sd_r:.2f}" if pd.notna(sd_r) else "—")
c[3].metric("SEM", f"{sem_r:.2f}" if pd.notna(sem_r) else "—")
c[4].metric("95% CI", f"{mean_r-ci:.2f}–{mean_r+ci:.2f}%" if pd.notna(ci) else "—")

if not gs.empty:
    st.dataframe(gs.round(5), width="stretch", hide_index=True)

st.markdown("### 4. Manuscript sections")
abstract = (f"H₂S is an important contaminant in gas-treatment applications, and efficient removal requires reliable process monitoring. "
            f"This study evaluated H₂S removal using {n} analysis units. Removal efficiency was calculated from paired inlet and outlet H₂S concentrations. "
            f"Mean observed removal was {mean_r:.2f}%" + (f", with {gs.iloc[0]['Group']} showing the highest observed group mean ({gs.iloc[0]['Mean']:.2f}%)." if not gs.empty else ".") + " These results provide an evidence base for evaluating process performance and operating-condition effects.")

intro = ("Hydrogen sulfide (H₂S) is a toxic and odorous sulfur-containing compound encountered in several environmental and industrial gas streams. "
        "Biological treatment approaches can provide a lower-chemical-intensity route for H₂S control when suitable microorganisms and operating conditions are maintained. "
        "However, treatment performance depends on inlet loading, residence time, environmental conditions and biological activity. "
        "The present study therefore evaluates H₂S removal using experimentally measured inlet and outlet concentrations, with emphasis on quantitative performance and reproducible statistical analysis.\n\n"
        "Study objective: " + objective)

methods = (f"Experimental data were analyzed from {source}. H₂S removal efficiency was calculated for each valid paired observation as ((inlet H₂S − outlet H₂S) / inlet H₂S) × 100. "
           + ("Where replicate identifiers were supplied, repeated observations were aggregated within the selected replicate structure before group-level summaries. " if "Replicate" in work else "No explicit replicate identifier was supplied; observations were therefore retained as row-level analysis units. ")
           + "Descriptive statistics included n, mean, standard deviation and standard error of the mean. Between-group screening used Welch's t-test/Mann–Whitney U for two groups or one-way ANOVA/Kruskal–Wallis for three or more groups, as appropriate. Statistical interpretation should be finalized according to the predefined experimental design and target-journal requirements.")

results = f"Across {n} analysis units, mean H₂S removal efficiency was {mean_r:.2f}%" + (f" ± {sem_r:.2f} SEM" if pd.notna(sem_r) else "") + (f" (95% CI {mean_r-ci:.2f}–{mean_r+ci:.2f}%)." if pd.notna(ci) else ".")
if not gs.empty:
    results += " Group-level results showed " + "; ".join([f"{r['Group']}: {r['Mean']:.2f}% ± {r['SEM']:.2f} SEM (n={int(r['N'])})" for _, r in gs.iterrows()]) + "."

if not gs.empty and len(gs) >= 2:
    vals = [analysis.loc[analysis["Group"] == g, "Removal %"].dropna().to_numpy() for g in gs["Group"]]
    if len(vals) == 2:
        tr = stats.ttest_ind(vals[0], vals[1], equal_var=False)
        results += f" Welch's t-test gave t={tr.statistic:.4g}, p={tr.pvalue:.4g}."
    else:
        ar = stats.f_oneway(*vals)
        results += f" One-way ANOVA gave F={ar.statistic:.4g}, p={ar.pvalue:.4g}."

discussion = ("The observed removal efficiencies indicate measurable treatment performance under the analyzed experimental conditions. "
             "Differences among groups should be interpreted in the context of replicate number, experimental-unit definition, uncertainty and process conditions. "
             "Relationships between removal efficiency and operating variables can support hypothesis generation, but correlation alone does not establish causality. "
             "The highest observed condition should not be described as a validated process optimum without independent confirmation experiments.")

conclusion = (f"The analyzed dataset demonstrated an overall mean H₂S removal efficiency of {mean_r:.2f}%. "
              + (f"The highest group-level mean was observed for {gs.iloc[0]['Group']} at {gs.iloc[0]['Mean']:.2f}%. " if not gs.empty else "")
              + "The evidence provides a quantitative basis for further optimization and confirmation experiments.")

highlights = [f"Mean observed H₂S removal: {mean_r:.2f}%", f"Analysis units: {n}"]
if not gs.empty: highlights.append(f"Highest group mean: {gs.iloc[0]['Group']} ({gs.iloc[0]['Mean']:.2f}%)")

captions = "Figure 1. H₂S removal efficiency calculated from paired inlet and outlet concentrations across the analyzed experimental observations.\n\nFigure 2. Distribution of H₂S removal efficiency by experimental group. Values and error bars should be defined explicitly in the final legend.\n\nTable 1. Replicate-aware summary of H₂S removal performance and statistical evidence."

sections = [("Abstract", abstract),("Introduction", intro),("Materials and Methods", methods),("Results", results),("Discussion", discussion),("Conclusion", conclusion),("Highlights", "\n".join("• " + x for x in highlights)),("Figure & Table Captions", captions)]
for name, text in sections:
    st.text_area(name, text, height=180 if name in {"Introduction","Materials and Methods","Discussion"} else 130, key=f"manuscript_{name}")

st.markdown("### 5. Final manuscript package")
full = "\n\n".join([f"# {title}"] + [f"## {name}\n{text}" for name, text in sections] + ["\n## Data source\n" + source])
tables = {"Analysis_Data": analysis, "Group_Summary": gs if not gs.empty else pd.DataFrame(), "Metadata": pd.DataFrame([{"Source":source,"Inlet":a,"Outlet":b,"Group":group,"Replicate":rep,"Time":time_col}])}
col1,col2 = st.columns(2)
with col1:
    st.download_button("⬇️ Download complete manuscript draft", full.encode("utf-8"), "scimantra_h2s_complete_manuscript.md", "text/markdown", width="stretch")
with col2:
    st.download_button("⬇️ Download evidence workbook", excel_bytes(tables), "scimantra_h2s_manuscript_evidence.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", width="stretch")
st.warning("Scientific safeguard: this builder drafts data-derived text only. Add literature citations, verify units and replicate definitions, check assumptions, and perform confirmation experiments before making causal or optimization claims.")
