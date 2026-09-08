from __future__ import annotations
import io
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
try:
    from src.scimantra.research_session import get_dataframe, metadata
except Exception:
    get_dataframe = lambda: None
    metadata = lambda: {}

st.set_page_config(page_title="H₂S Publication Figure Engine", page_icon="📊", layout="wide")
st.title("📊 H₂S Publication Figure Engine")
st.caption("Publication-ready figures with individual observations, uncertainty and high-resolution export.")
current_df = get_dataframe()
meta = metadata()
source = meta.get("filename", "Current Data Analyzer dataset") if isinstance(meta, dict) else "Current Data Analyzer dataset"
uploaded = st.file_uploader("Upload CSV/Excel, or use the current Data Analyzer dataset", type=["csv", "xlsx", "xls"])
df = None
if uploaded:
    if uploaded.name.lower().endswith(".csv"):
        df = pd.read_csv(uploaded)
    else:
        sheets = pd.read_excel(uploaded, sheet_name=None)
        chosen = max(sheets, key=lambda s: sheets[s].select_dtypes(include="number").size)
        df = sheets[chosen]
        source = f"{uploaded.name} | {chosen}"
elif current_df is not None and not current_df.empty:
    df = current_df.copy()
if df is None or df.empty:
    st.info("Load a dataset through Data Analyzer or upload one here.")
    st.stop()
numeric = df.select_dtypes(include="number").columns.tolist()
all_cols = list(df.columns)
def guess(options, words):
    for c in options:
        if any(w in str(c).lower() for w in words): return c
    return options[0] if options else None
def idx(options, value): return options.index(value) if value in options else 0

st.markdown("### 1. Figure configuration")
figure_type = st.selectbox("Figure", ["Inlet vs outlet H₂S", "H₂S removal by treatment", "Removal vs EBRT", "Removal vs loading", "Removal vs pH", "Time course"])
inlet_default = guess(numeric, ["inlet", "influent", "input"])
outlet_default = guess(numeric, ["outlet", "effluent", "output"])
removal_default = guess(numeric, ["removal", "rem_%", "removal_percent"])
c1, c2 = st.columns(2)
with c1:
    inlet = st.selectbox("Inlet H₂S", ["(none)"] + numeric, index=idx(["(none)"] + numeric, inlet_default))
    outlet = st.selectbox("Outlet H₂S", ["(none)"] + numeric, index=idx(["(none)"] + numeric, outlet_default))
    removal = st.selectbox("Removal %", ["(none)"] + numeric, index=idx(["(none)"] + numeric, removal_default))
with c2:
    group = st.selectbox("Treatment / group", ["(none)"] + all_cols)
    replicate = st.selectbox("Replicate ID", ["(none)"] + all_cols)
    time_col = st.selectbox("Time", ["(none)"] + all_cols)
other_numeric = [c for c in numeric if c not in {inlet, outlet, removal}]
variable = None
if figure_type == "Removal vs EBRT": variable = st.selectbox("EBRT", ["(none)"] + other_numeric, index=idx(["(none)"] + other_numeric, guess(other_numeric, ["ebrt", "retention"])))
elif figure_type == "Removal vs loading": variable = st.selectbox("Loading", ["(none)"] + other_numeric, index=idx(["(none)"] + other_numeric, guess(other_numeric, ["loading", "load"])))
elif figure_type == "Removal vs pH": variable = st.selectbox("pH", ["(none)"] + other_numeric, index=idx(["(none)"] + other_numeric, guess(other_numeric, ["ph"])))
elif figure_type == "Time course": variable = st.selectbox("Time", ["(none)"] + numeric, index=idx(["(none)"] + numeric, time_col if time_col != "(none)" else guess(numeric, ["time", "day", "hour"])))
show_points = st.checkbox("Show individual observations", True)
error_type = st.selectbox("Summary error bars", ["95% CI", "SEM", "SD"])
dpi = st.selectbox("Export resolution", [300, 600, 1200], index=1)
width = st.number_input("Figure width (inches)", 4.0, 14.0, 7.0, 0.5)
height = st.number_input("Figure height (inches)", 3.0, 12.0, 5.0, 0.5)
work = df.copy()
if inlet != "(none)" and outlet != "(none)": work["__Removal"] = (pd.to_numeric(work[inlet], errors="coerce") - pd.to_numeric(work[outlet], errors="coerce")) / pd.to_numeric(work[inlet], errors="coerce").replace(0, np.nan) * 100
elif removal != "(none)": work["__Removal"] = pd.to_numeric(work[removal], errors="coerce")
else: work["__Removal"] = np.nan

def stats_for(values):
    x = pd.to_numeric(values, errors="coerce").dropna(); n = len(x)
    if n == 0: return np.nan, np.nan, 0
    mean = x.mean(); sd = x.std(ddof=1) if n > 1 else np.nan; sem = sd / np.sqrt(n) if n > 1 else np.nan; ci = 1.96 * sem if n > 1 else np.nan
    return mean, (ci if error_type == "95% CI" else sem if error_type == "SEM" else sd), n
fig, ax = plt.subplots(figsize=(width, height), dpi=dpi)
if figure_type == "Inlet vs outlet H₂S":
    if inlet == "(none)" or outlet == "(none)": st.warning("Select inlet and outlet columns."); st.stop()
    d = work[[inlet, outlet]].apply(pd.to_numeric, errors="coerce").dropna(); labels=["Inlet", "Outlet"]
    means=[]; errs=[]
    for c in [inlet, outlet]:
        m,e,n=stats_for(d[c]); means.append(m); errs.append(e)
    ax.bar(range(2), means, yerr=errs, capsize=5)
    if show_points:
        rng=np.random.default_rng(42)
        for i,c in enumerate([inlet,outlet]): ax.scatter(np.full(len(d),i)+rng.uniform(-.08,.08,len(d)),d[c],alpha=.7,s=25)
    ax.set_xticks(range(2),labels); ax.set_ylabel("H₂S concentration"); ax.set_title("Inlet vs outlet H₂S"); ax.text(.02,.97,f"n = {len(d)}",transform=ax.transAxes,va="top")
elif figure_type == "H₂S removal by treatment":
    if group == "(none)": st.warning("Select a treatment/group column."); st.stop()
    d=work[[group,"__Removal"]].dropna(); groups=list(d[group].astype(str).unique())
    if not groups: st.warning("No valid observations."); st.stop()
    data=[d.loc[d[group].astype(str)==g,"__Removal"].astype(float).values for g in groups]
    ax.boxplot(data, labels=groups, showfliers=False)
    if show_points:
        rng=np.random.default_rng(42)
        for i,v in enumerate(data,1): ax.scatter(np.full(len(v),i)+rng.uniform(-.08,.08,len(v)),v,alpha=.7,s=24)
    for i,v in enumerate(data,1): ax.text(i,np.nanmax(v),f"n={len(v)}",ha="center",va="bottom",fontsize=9)
    ax.set_ylabel("H₂S removal (%)"); ax.set_title("H₂S removal by treatment"); ax.tick_params(axis="x",rotation=25)
else:
    if variable is None or variable == "(none)": st.warning("Select the requested x-axis variable."); st.stop()
    d=work[[variable,"__Removal"]].apply(pd.to_numeric,errors="coerce").dropna()
    if d.empty: st.warning("No valid observations."); st.stop()
    x=d[variable].to_numpy(float); y=d["__Removal"].to_numpy(float); ax.scatter(x,y,alpha=.75,s=30,label="Observations")
    if len(d)>=3 and np.ptp(x)>0:
        slope,intercept=np.polyfit(x,y,1); xx=np.linspace(x.min(),x.max(),100); ax.plot(xx,intercept+slope*xx,linewidth=2,label="OLS fit")
        r=np.corrcoef(x,y)[0,1]; ax.text(.02,.97,f"n = {len(d)}\nr = {r:.3f}\nR² = {r*r:.3f}",transform=ax.transAxes,va="top")
    ax.set_xlabel(str(variable)); ax.set_ylabel("H₂S removal (%)"); ax.set_title(figure_type); ax.legend()
fig.tight_layout(); st.pyplot(fig)
st.markdown("### 2. Export")
png=io.BytesIO(); fig.savefig(png,format="png",dpi=dpi,bbox_inches="tight"); png.seek(0)
svg=io.BytesIO(); fig.savefig(svg,format="svg",bbox_inches="tight"); svg.seek(0)
c1,c2=st.columns(2)
with c1: st.download_button(f"⬇️ PNG ({dpi} DPI)",png.getvalue(),"h2s_publication_figure.png","image/png",width="stretch")
with c2: st.download_button("⬇️ Vector SVG",svg.getvalue(),"h2s_publication_figure.svg","image/svg+xml",width="stretch")
st.caption(f"Source: {source}. Error bars: {error_type}. Always report the experimental unit and replication structure in the caption.")
st.warning("This engine visualizes verified observations; it does not determine biological independence or statistical validity automatically.")
