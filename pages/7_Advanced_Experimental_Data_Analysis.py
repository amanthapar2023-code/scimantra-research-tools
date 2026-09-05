import io
import math
import numpy as np
import pandas as pd
import streamlit as st
from scipy import stats
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Advanced Experimental Data Analysis", page_icon="📊", layout="wide")

st.title("📊 Advanced Experimental Data Analysis")
st.caption("Replicate-aware statistics, time-series analysis, regression, effect sizes and research-grade visualization.")
st.info("Research aid: statistical choices must match the experimental design. Distinguish biological/independent replicates from technical measurements before drawing biological conclusions.")

uploaded = st.file_uploader("Upload Excel or CSV dataset", type=["xlsx", "csv"])
if uploaded is None:
    st.markdown("### Recommended dataset structure")
    st.dataframe(pd.DataFrame([
        {"Group":"Control","Replicate":"B1","Technical":"T1","Time":0,"Value":10.0},
        {"Group":"Control","Replicate":"B1","Technical":"T2","Time":0,"Value":10.5},
        {"Group":"Treatment","Replicate":"B1","Technical":"T1","Time":0,"Value":8.0},
        {"Group":"Treatment","Replicate":"B1","Technical":"T2","Time":0,"Value":8.4},
    ]), use_container_width=True)
    st.stop()

try:
    df = pd.read_csv(uploaded) if uploaded.name.lower().endswith(".csv") else pd.read_excel(uploaded)
except Exception as exc:
    st.error(f"Could not read the file: {exc}")
    st.stop()

st.success(f"Loaded {len(df):,} rows × {len(df.columns):,} columns")

with st.expander("1. Data quality check", expanded=True):
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Rows", f"{len(df):,}")
    c2.metric("Columns", f"{len(df.columns):,}")
    c3.metric("Missing cells", f"{int(df.isna().sum().sum()):,}")
    c4.metric("Duplicate rows", f"{int(df.duplicated().sum()):,}")
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    if numeric_cols:
        st.dataframe(df[numeric_cols].describe().T, use_container_width=True)
    else:
        st.warning("No numeric columns were detected.")
    st.dataframe(df.head(50), use_container_width=True)

numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
if not numeric_cols:
    st.stop()

st.sidebar.header("Analysis setup")
value_col = st.sidebar.selectbox("Measurement / response", numeric_cols)
other_numeric = [c for c in numeric_cols if c != value_col]
time_candidates = [c for c in df.columns if c != value_col and ("time" in str(c).lower() or "day" in str(c).lower() or "hour" in str(c).lower())]
time_col = st.sidebar.selectbox("Time column (optional)", ["None"] + time_candidates + other_numeric)
time_col = None if time_col == "None" else time_col
group_candidates = [c for c in df.columns if c != value_col and df[c].nunique(dropna=True) <= min(30, max(2, len(df)//2))]
group_col = st.sidebar.selectbox("Experimental group (optional)", ["None"] + group_candidates)
group_col = None if group_col == "None" else group_col
rep_candidates = [c for c in df.columns if c != value_col and ("rep" in str(c).lower() or "sample" in str(c).lower() or "isolate" in str(c).lower())]
rep_col = st.sidebar.selectbox("Independent/biological replicate ID (optional)", ["None"] + rep_candidates)
rep_col = None if rep_col == "None" else rep_col
tech_candidates = [c for c in df.columns if c != value_col and ("tech" in str(c).lower() or "technical" in str(c).lower())]
tech_col = st.sidebar.selectbox("Technical replicate ID (optional)", ["None"] + tech_candidates)
tech_col = None if tech_col == "None" else tech_col

work = df.copy()
work["__value"] = pd.to_numeric(work[value_col], errors="coerce")
work = work[np.isfinite(work["__value"])].copy()

if group_col:
    work["__group"] = work[group_col].astype(str)
else:
    work["__group"] = "All observations"

if time_col:
    work["__time"] = pd.to_numeric(work[time_col], errors="coerce")

st.subheader("2. Descriptive statistics")
if group_col:
    summary = work.groupby("__group")["__value"].agg(n="count", mean="mean", SD="std", median="median", min="min", max="max").reset_index()
    summary["SEM"] = work.groupby("__group")["__value"].sem().values
    summary["CV_%"] = summary["SD"].div(summary["mean"].replace(0,np.nan)).abs()*100
else:
    x=work["__value"]
    summary=pd.DataFrame([{"Group":"All observations","n":len(x),"mean":x.mean(),"SD":x.std(ddof=1),"SEM":x.sem() if len(x)>1 else np.nan,"median":x.median(),"min":x.min(),"max":x.max(),"CV_%":abs(x.std(ddof=1)/x.mean()*100) if len(x)>1 and x.mean()!=0 else np.nan}])
st.dataframe(summary, use_container_width=True)

st.subheader("3. Replicate-aware summary")
if rep_col:
    rep_summary = work.groupby(["__group", rep_col])["__value"].agg(n="count", mean="mean", SD="std").reset_index()
    st.dataframe(rep_summary, use_container_width=True)
    if tech_col:
        tech_summary = work.groupby(["__group", rep_col, tech_col])["__value"].mean().reset_index(name="technical_mean")
        collapsed = tech_summary.groupby(["__group", rep_col])["technical_mean"].mean().reset_index(name="biological_replicate_mean")
        st.caption("Technical measurements are first averaged within independent replicate IDs; group-level statistics can then be based on independent replicates.")
        st.dataframe(collapsed, use_container_width=True)
        analysis_df = collapsed.rename(columns={"biological_replicate_mean":"__value"})
    else:
        analysis_df = rep_summary.rename(columns={"mean":"__value"})
else:
    analysis_df = work.copy()
    st.warning("No independent/biological replicate ID was selected. Inferential statistics below will use observations as supplied.")

def cohen_d(a,b):
    a=np.asarray(a,float); b=np.asarray(b,float); na,nb=len(a),len(b)
    if na<2 or nb<2: return np.nan
    pooled=np.sqrt(((na-1)*np.var(a,ddof=1)+(nb-1)*np.var(b,ddof=1))/(na+nb-2))
    return (np.mean(a)-np.mean(b))/pooled if pooled else np.nan

st.subheader("4. Statistical tests")
if group_col:
    groups = [g["__value"].dropna().to_numpy() for _,g in analysis_df.groupby("__group") if len(g["__value"].dropna())]
    names = [str(k) for k,_ in analysis_df.groupby("__group") if len(_["__value"].dropna())]
    if len(groups)==2:
        r=stats.ttest_ind(groups[0],groups[1],equal_var=False,nan_policy="omit")
        d=cohen_d(groups[0],groups[1])
        c=st.columns(4); c[0].metric("Welch t",f"{r.statistic:.5g}"); c[1].metric("p-value",f"{r.pvalue:.5g}"); c[2].metric("Cohen's d",f"{d:.5g}" if np.isfinite(d) else "N/A"); c[3].metric("Interpretation","Significant" if r.pvalue<0.05 else "Not significant")
        st.caption("Two-sided Welch independent-samples t-test. Check independence and distributional assumptions before formal use.")
    elif len(groups)>=3:
        r=stats.f_oneway(*groups)
        c=st.columns(3); c[0].metric("One-way ANOVA F",f"{r.statistic:.5g}"); c[1].metric("p-value",f"{r.pvalue:.5g}"); c[2].metric("Interpretation","Significant" if r.pvalue<0.05 else "Not significant")
        try:
            tukey=stats.tukey_hsd(*groups)
            pairs=[]
            for i in range(len(names)):
                for j in range(i+1,len(names)):
                    pairs.append({"Group 1":names[i],"Group 2":names[j],"Mean difference":groups[i].mean()-groups[j].mean(),"p-value":tukey.pvalue[i,j],"Significant (0.05)":bool(tukey.pvalue[i,j]<0.05)})
            st.markdown("**Tukey HSD post-hoc comparisons**")
            st.dataframe(pd.DataFrame(pairs),use_container_width=True)
        except Exception as exc:
            st.warning(f"Post-hoc comparison unavailable for this dataset: {exc}")
    else:
        st.info("Select an experimental group column with at least two groups containing numeric observations.")
else:
    st.info("Select an experimental group column in the sidebar to enable between-group inference.")

st.subheader("5. Correlation and regression")
if len(other_numeric)>=1:
    predictor=st.selectbox("Predictor variable",other_numeric)
    xy=pd.DataFrame({"x":pd.to_numeric(df[predictor],errors="coerce"),"y":pd.to_numeric(df[value_col],errors="coerce")}).dropna()
    if len(xy)>=3:
        pear=stats.pearsonr(xy.x,xy.y); spear=stats.spearmanr(xy.x,xy.y); fit=stats.linregress(xy.x,xy.y); ci=stats.t.interval(0.95,len(xy)-2,loc=fit.slope,scale=fit.stderr) if len(xy)>2 else (np.nan,np.nan)
        c=st.columns(5); c[0].metric("Pearson r",f"{pear.statistic:.5g}"); c[1].metric("Pearson p",f"{pear.pvalue:.5g}"); c[2].metric("Spearman ρ",f"{spear.statistic:.5g}"); c[3].metric("R²",f"{fit.rvalue**2:.5g}"); c[4].metric("Slope 95% CI",f"{ci[0]:.4g} to {ci[1]:.4g}")
        xx=np.linspace(xy.x.min(),xy.x.max(),100); fig=go.Figure([go.Scatter(x=xy.x,y=xy.y,mode="markers",name="Observations"),go.Scatter(x=xx,y=fit.intercept+fit.slope*xx,mode="lines",name="Linear fit")]); fig.update_layout(xaxis_title=predictor,yaxis_title=value_col,title="Regression with observations"); st.plotly_chart(fig,use_container_width=True)
    else: st.warning("Need at least three paired numeric observations.")

st.subheader("6. Time-series / growth analysis")
if time_col:
    ts=work.dropna(subset=["__time"]).copy()
    if group_col:
        plot_df=ts.groupby(["__group","__time"])["__value"].agg(mean="mean",SD="std",n="count").reset_index(); plot_df["SEM"]=plot_df["SD"]/np.sqrt(plot_df["n"])
        fig=px.line(plot_df,x="__time",y="mean",color="__group",markers=True,error_y="SEM",title=f"{value_col} over time (mean ± SEM)"); fig.update_layout(xaxis_title=time_col,yaxis_title=value_col); st.plotly_chart(fig,use_container_width=True)
    else:
        plot_df=ts.groupby("__time")["__value"].agg(mean="mean",SD="std",n="count").reset_index(); plot_df["SEM"]=plot_df["SD"]/np.sqrt(plot_df["n"]); fig=px.line(plot_df,x="__time",y="mean",markers=True,error_y="SEM",title=f"{value_col} over time (mean ± SEM)"); st.plotly_chart(fig,use_container_width=True)
    st.dataframe(plot_df,use_container_width=True)
    if group_col and len(plot_df)>=3:
        st.caption("For repeated-measures or longitudinal experiments, use an appropriate repeated-measures/mixed-effects model rather than treating all time points as independent observations.")
else:
    st.info("Select a time/day/hour column in the sidebar to enable time-series analysis.")

st.subheader("7. Publication-oriented visualization")
plot_group = group_col if group_col else None
fig=px.box(work,x="__group",y="__value",points="all",color=plot_group,title=f"{value_col}: distribution and individual observations")
fig.update_layout(xaxis_title=group_col or "Dataset",yaxis_title=value_col)
st.plotly_chart(fig,use_container_width=True)

st.subheader("8. Automated research interpretation")
if group_col and len(groups)>=2:
    means=analysis_df.groupby("__group")["__value"].mean().sort_values(ascending=False)
    st.write(f"Highest observed group mean: **{means.index[0]}** ({means.iloc[0]:.5g}).")
    if len(groups)==2:
        direction="higher" if means.iloc[0]>means.iloc[1] else "lower"
        st.write(f"The first-ranked group mean is {direction} than the other group. Statistical significance should be interpreted together with effect size and experimental design.")
    elif len(groups)>=3:
        st.write("For three or more groups, use the ANOVA result together with Tukey post-hoc comparisons to identify which groups differ.")
if other_numeric:
    st.write("Correlation coefficients describe association, not causation. R² describes variance explained by the fitted linear model, not proof of mechanism.")

st.subheader("9. Export analysis tables")
summary_export=summary.copy()
summary_csv=summary_export.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Download descriptive summary (CSV)",summary_csv,"advanced_descriptive_summary.csv","text/csv")
if rep_col:
    rep_csv=rep_summary.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download replicate summary (CSV)",rep_csv,"replicate_summary.csv","text/csv")

with st.expander("Statistical reporting checklist"):
    st.markdown("""
- Define the experimental unit and independent/biological replicates.
- Distinguish technical repeats from independent biological replicates.
- Report n, mean, SD/SEM and the exact statistical test.
- Report effect size and confidence intervals where appropriate.
- For ANOVA, report the omnibus test and suitable post-hoc comparisons.
- Check assumptions and consider transformations/non-parametric or mixed-effects methods when justified.
- Do not interpret p < 0.05 as proof of biological importance.
- Keep raw data, analysis choices and software/version information reproducible.
""")

st.caption("SciMantra Research Tools • Educational/research aid. Verify statistical assumptions and methods against your study design, SOP, disciplinary guidance and reporting standard before publication.")
