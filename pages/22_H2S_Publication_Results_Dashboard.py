from __future__ import annotations

import io
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from scipy import stats
from src.scimantra.research_session import get_dataframe, metadata

st.set_page_config(page_title="H₂S Publication Results Dashboard", page_icon="🧪", layout="wide")

st.title("🧪 H₂S Publication Results Dashboard")
st.caption("Replicate-aware summary, statistical screening, relationship analysis and publication-oriented figures. Results are evidence summaries; choose the final statistical model according to your experimental design.")


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
    file = st.file_uploader("Upload H₂S experimental dataset", type=["xlsx", "csv"])
    if not file:
        st.info("Upload data here, or first open Data Analyzer and select your H₂S worksheet.")
        st.stop()
    if file.name.lower().endswith(".csv"):
        df = pd.read_csv(file)
    else:
        book = pd.ExcelFile(file)
        sheet = st.selectbox("Worksheet", book.sheet_names)
        df = pd.read_excel(book, sheet_name=sheet)
else:
    meta = metadata()
    st.success(f"Using current Data Analyzer dataset: **{meta.get('filename','dataset')}**" + (f" • {meta['sheet']}" if meta.get("sheet") else ""))

h2s = find(df, ["h2s", "hydrogen sulfide", "sulfide", "sulphide"])
inlet = [c for c in h2s if any(k in str(c).lower() for k in ["inlet", "influent", "input", "initial"])]
outlet = [c for c in h2s if any(k in str(c).lower() for k in ["outlet", "effluent", "output", "final"])]
removal = find(df, ["removal efficiency", "removal %", "h2s removal"])
load = find(df, ["inlet h2s load", "h2s loading", "loading"])
ebrt = find(df, ["ebrt"])
ph = find(df, ["ph"])
groups = find(df, ["treatment", "reactor", "condition", "group"])

if not h2s:
    st.warning("No H₂S-like columns detected. Rename concentration fields clearly and reload.")
    st.stop()

st.markdown("### 1. Define analysis fields")
a = st.selectbox("Inlet / influent H₂S", inlet or h2s)
b = st.selectbox("Outlet / effluent H₂S", outlet or [c for c in h2s if c != a] or h2s)
group = st.selectbox("Experimental group / treatment", ["None"] + groups)
time = find(df, ["time", "hour", "hr", "day", "minute", "min"])
time_col = st.selectbox("Time / run variable", ["None"] + time)

work = pd.DataFrame({"Inlet H₂S": num(df, a), "Outlet H₂S": num(df, b)})
if group != "None": work["Group"] = df[group]
if time_col != "None": work["Time"] = df[time_col]
work = work.replace([np.inf, -np.inf], np.nan)
work = work.dropna(subset=["Inlet H₂S", "Outlet H₂S"])
work = work[work["Inlet H₂S"] != 0].copy()
work["Removal %"] = (work["Inlet H₂S"] - work["Outlet H₂S"]) / work["Inlet H₂S"] * 100

for label, cols in [("Loading", load), ("EBRT", ebrt), ("pH", ph)]:
    if cols:
        c = st.selectbox(f"{label} variable (optional)", ["None"] + cols, key=f"pub_{label}")
        if c != "None": work[label] = num(df, c).reindex(work.index)

st.markdown("### 2. Study-level evidence")
n = len(work)
mean_r = work["Removal %"].mean()
sd_r = work["Removal %"].std(ddof=1) if n > 1 else np.nan
sem_r = sd_r / np.sqrt(n) if n > 1 else np.nan
ci = stats.t.ppf(0.975, n - 1) * sem_r if n > 1 else np.nan
c = st.columns(5)
c[0].metric("Paired observations", n)
c[1].metric("Mean removal", f"{mean_r:.2f}%")
c[2].metric("SD", f"{sd_r:.2f}" if pd.notna(sd_r) else "—")
c[3].metric("SEM", f"{sem_r:.2f}" if pd.notna(sem_r) else "—")
c[4].metric("95% CI", f"{mean_r-ci:.2f} to {mean_r+ci:.2f}%" if pd.notna(ci) else "—")

st.markdown("### 3. Replicate-aware group results")
tables = {"Paired_Data": work.copy()}
if "Group" in work:
    g = work.groupby("Group")["Removal %"]
    summary = g.agg(N="count", Mean="mean", SD="std", Median="median", Min="min", Max="max").reset_index()
    summary["SEM"] = summary["SD"] / np.sqrt(summary["N"])
    summary["95% CI low"] = summary.apply(lambda r: r["Mean"] - stats.t.ppf(.975, r["N"]-1)*r["SEM"] if r["N"] > 1 else np.nan, axis=1)
    summary["95% CI high"] = summary.apply(lambda r: r["Mean"] + stats.t.ppf(.975, r["N"]-1)*r["SEM"] if r["N"] > 1 else np.nan, axis=1)
    summary["CV %"] = summary["SD"] / summary["Mean"].replace(0, np.nan) * 100
    summary = summary.sort_values("Mean", ascending=False).reset_index(drop=True)
    st.dataframe(summary.round(5), width="stretch", hide_index=True)
    tables["Group_Summary"] = summary
    st.plotly_chart(px.bar(summary, x="Group", y="Mean", error_y="SEM", title="Mean H₂S removal efficiency by experimental group"), width="stretch")
    st.caption("Bars show mean removal; error bars are SEM. For manuscripts, use the error convention required by your target journal and report n explicitly.")

    unique_groups = list(g.groups.keys())
    if len(unique_groups) == 2:
        vals = [g.get_group(k).dropna().to_numpy() for k in unique_groups]
        t = stats.ttest_ind(vals[0], vals[1], equal_var=False)
        u = stats.mannwhitneyu(vals[0], vals[1], alternative="two-sided")
        pooled = np.sqrt(((len(vals[0])-1)*np.var(vals[0],ddof=1)+(len(vals[1])-1)*np.var(vals[1],ddof=1))/(len(vals[0])+len(vals[1])-2)) if len(vals[0])+len(vals[1])>2 else np.nan
        d = (np.mean(vals[0])-np.mean(vals[1]))/pooled if pooled and pooled>0 else np.nan
        st.markdown("#### Two-group screening")
        q = pd.DataFrame([{ "Group A": unique_groups[0], "Group B": unique_groups[1], "Welch t": t.statistic, "Welch p": t.pvalue, "Mann–Whitney U": u.statistic, "Mann–Whitney p": u.pvalue, "Cohen d": d }])
        st.dataframe(q.round(6), width="stretch", hide_index=True)
        tables["Two_Group_Test"] = q
    elif len(unique_groups) >= 3:
        vals = [g.get_group(k).dropna().to_numpy() for k in unique_groups]
        ares = stats.f_oneway(*vals)
        kres = stats.kruskal(*vals)
        q = pd.DataFrame([{ "Groups": len(unique_groups), "ANOVA F": ares.statistic, "ANOVA p": ares.pvalue, "Kruskal H": kres.statistic, "Kruskal p": kres.pvalue }])
        st.markdown("#### Multi-group screening")
        st.dataframe(q.round(6), width="stretch", hide_index=True)
        tables["Multi_Group_Test"] = q

st.markdown("### 4. Publication figures")
fig1 = px.scatter(work, x="Inlet H₂S", y="Outlet H₂S", trendline="ols", title="Influent vs effluent H₂S", hover_data=["Removal %"])
fig1.update_layout(height=500)
st.plotly_chart(fig1, width="stretch")

if "Group" in work:
    fig2 = px.box(work, x="Group", y="Removal %", points="all", title="H₂S removal efficiency by experimental group")
    fig2.update_layout(height=500)
    st.plotly_chart(fig2, width="stretch")

if "EBRT" in work:
    fig3 = px.scatter(work, x="EBRT", y="Removal %", trendline="ols", title="Removal efficiency vs EBRT")
    fig3.update_layout(height=500)
    st.plotly_chart(fig3, width="stretch")

if "Loading" in work:
    fig4 = px.scatter(work, x="Loading", y="Removal %", trendline="ols", title="Removal efficiency vs H₂S loading")
    fig4.update_layout(height=500)
    st.plotly_chart(fig4, width="stretch")

if "pH" in work:
    fig5 = px.scatter(work, x="pH", y="Removal %", trendline="ols", title="Removal efficiency vs pH")
    fig5.update_layout(height=500)
    st.plotly_chart(fig5, width="stretch")

st.markdown("### 5. Time-course")
if "Time" in work:
    plot = work.sort_values("Time")
    st.plotly_chart(px.line(plot, x="Time", y="Removal %", color="Group" if "Group" in work else None, markers=True, title="H₂S removal efficiency over time"), width="stretch")
else:
    st.info("Select a time/run variable above to generate a time-course figure.")

st.markdown("### 6. Relationship statistics")
relationship_rows = []
response = "Removal %"
for xcol in [c for c in ["Inlet H₂S", "Outlet H₂S", "Loading", "EBRT", "pH"] if c in work]:
    pair = work[[xcol, response]].dropna()
    if len(pair) >= 3 and pair[xcol].nunique() >= 2:
        lr = stats.linregress(pair[xcol], pair[response])
        sr = stats.spearmanr(pair[xcol], pair[response])
        relationship_rows.append({"Predictor": xcol, "N": len(pair), "Pearson r": lr.rvalue, "R²": lr.rvalue**2, "Pearson p": lr.pvalue, "Spearman rho": sr.statistic, "Spearman p": sr.pvalue, "Slope": lr.slope})
rel = pd.DataFrame(relationship_rows)
if not rel.empty:
    st.dataframe(rel.round(6), width="stretch", hide_index=True)
    tables["Relationships"] = rel
else:
    st.info("Add operating variables such as EBRT, loading or pH to generate relationship statistics.")

st.markdown("### 7. Manuscript result draft")
if "Group" in work and 'summary' in locals() and len(summary):
    top = summary.iloc[0]
    draft = (f"The analyzed experiments showed a mean H₂S removal efficiency of {mean_r:.2f} ± {sem_r:.2f}% (mean ± SEM; n={n}). "
             f"Among the experimental groups, {top['Group']} had the highest mean removal ({top['Mean']:.2f} ± {top['SEM']:.2f}%; n={int(top['N'])}).")
else:
    draft = f"The analyzed experiments showed a mean H₂S removal efficiency of {mean_r:.2f} ± {sem_r:.2f}% (mean ± SEM; n={n})."
st.text_area("Draft", draft, height=120)
st.caption("Edit to match your predefined experimental design, replicate definition, units, statistical model and journal reporting requirements. Do not infer causality from correlation or label the highest observed value as a validated optimum without confirmation experiments.")

st.markdown("### 8. Export evidence package")
st.download_button("⬇️ Download publication evidence workbook", excel_bytes(tables), "scimantra_h2s_publication_evidence.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", width="stretch")
st.download_button("⬇️ Download relationship statistics", rel.to_csv(index=False).encode() if not rel.empty else b"Predictor,N\n", "scimantra_h2s_relationships.csv", "text/csv", width="stretch")
