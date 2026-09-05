import io
import math
import numpy as np
import pandas as pd
import streamlit as st
from scipy import stats
from scipy.optimize import curve_fit
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="H₂S Research Analysis Suite", page_icon="📊", layout="wide")

# -----------------------------------------------------------------------------
# Research-specific knowledge base assembled from the user's previously shared
# research reports, PR material and analysis work. These are labelled by status
# so reported/preliminary/illustrative values are never silently treated as raw
# replicated observations.
# -----------------------------------------------------------------------------
RESEARCH_PROFILE = {
    "title": "Development of an Integrated Biological–Photocatalytic Reactor for Odorous Gases Abatement",
    "model_pollutant": "H₂S",
    "selected_isolate": "I-Tn2",
    "isolates_screened": 9,
    "column_height_mm": 300,
    "column_diameter_mm": 50,
    "geometric_volume_L": 0.589,
    "planned_ebrt_s": [20, 40, 60, 80, 90],
    "planned_h2s_ppm": [5, 10, 20, 50, 100],
    "operating_temperature_C": 30,
    "planned_ph": [5, 7, 9],
    "objectives": [
        "Fabricate biological and photocatalytic reactors for odorous-gas degradation",
        "Optimize process conditions for maximized abatement",
        "Perform techno-economic analysis of biological/photocatalytic hybrid systems",
    ],
}

# Values explicitly reported in the PR/viva material. They are intentionally
# kept separate from uploaded raw data.
REPORTED_RESULTS = pd.DataFrame([
    {"Analysis": "Isolate screening", "Metric": "Selected isolate", "Value": "I-Tn2", "Status": "Reported PR result"},
    {"Analysis": "Isolate screening", "Metric": "Number of isolates", "Value": "9", "Status": "Reported PR result"},
    {"Analysis": "I-Tn2 screening", "Metric": "Maximum/selected OD₆₀₀", "Value": "~1.0", "Status": "Reported PR result"},
    {"Analysis": "I-Tn2 screening", "Metric": "Final pH", "Value": "~2.5", "Status": "Reported PR result"},
    {"Analysis": "EBRT study", "Metric": "Removal efficiency", "Value": "48.2% → 97.3%", "Status": "Reported PR result"},
    {"Analysis": "H₂S loading study", "Metric": "Removal efficiency", "Value": "97.4% → 83.7%", "Status": "Reported PR result"},
    {"Analysis": "7-day operation", "Metric": "Removal efficiency", "Value": "~90% → ~94%", "Status": "Reported PR result"},
    {"Analysis": "7-day operation", "Metric": "Outlet H₂S", "Value": "~10 → ~6 ppm", "Status": "Reported PR result"},
    {"Analysis": "Biological control", "Metric": "Inoculated removal", "Value": "~94%", "Status": "Reported PR result"},
    {"Analysis": "Abiotic control", "Metric": "Uninoculated removal", "Value": "~28%", "Status": "Reported PR result"},
    {"Analysis": "Biological control", "Metric": "Dissolved sulfide", "Value": "50 → 8 mg/L", "Status": "Reported PR result"},
    {"Analysis": "Biological control", "Metric": "Sulfate", "Value": "65 → 285 mg/L", "Status": "Reported PR result"},
    {"Analysis": "Biological control", "Metric": "pH", "Value": "7.5 → 2.5", "Status": "Reported PR result"},
    {"Analysis": "Preliminary observation", "Metric": "H₂S", "Value": "60 → 2 ppm; 96.67%", "Status": "Preliminary/viva observation; not automatically treated as replicated raw data"},
])

BIOCHEMICAL_PROFILE = pd.DataFrame([
    {"Parameter": "Gram staining", "Research note": "7/9 isolates reported Gram-positive; 2/9 Gram-negative", "Status": "Reported"},
    {"Parameter": "Morphology", "Research note": "Bacillus/coccus morphologies represented; one mixed morphology reported", "Status": "Reported"},
    {"Parameter": "Catalase", "Research note": "Among the most prevalent positive characteristics", "Status": "Reported"},
    {"Parameter": "Citrate", "Research note": "Among the most prevalent positive characteristics", "Status": "Reported"},
    {"Parameter": "Indole", "Research note": "Variable among isolates", "Status": "Reported"},
    {"Parameter": "Oxidase", "Research note": "Variable among isolates", "Status": "Reported"},
    {"Parameter": "VP", "Research note": "All nine isolates reported VP-negative", "Status": "Reported"},
    {"Parameter": "Additional planned characterization", "Research note": "Physiology, tolerance, microscopy and molecular/taxonomic identification", "Status": "Planned"},
])

METHODS_PROFILE = pd.DataFrame([
    {"Area": "H₂S generation", "Technical detail": "Na₂S + 2HCl → H₂S + 2NaCl; controlled gas generation and dilution", "Evidence status": "Established platform"},
    {"Area": "Reactor", "Technical detail": "Packed-bed column; approximately 300 mm height × 50 mm diameter; geometric volume ~0.589 L", "Evidence status": "Established platform"},
    {"Area": "Support", "Technical detail": "Glass-bead trial followed by clay-bead optimization after inadequate biofilm establishment", "Evidence status": "Experimental decision"},
    {"Area": "Gas monitoring", "Technical detail": "Inlet/outlet H₂S monitoring; gas flow/EBRT and pressure drop", "Evidence status": "Established/ongoing"},
    {"Area": "Liquid sulfur analysis", "Technical detail": "Dissolved sulfide, sulfate and pH; elemental sulfur where available", "Evidence status": "Ongoing/expanded"},
    {"Area": "Microbiology", "Technical detail": "STP-derived isolates; enrichment, purification, biochemical characterization and screening", "Evidence status": "Completed/ongoing"},
    {"Area": "Photocatalysis", "Technical detail": "TiO₂/Fe-TiO₂/ZnO and waste-derived catalyst pathway; UV-DRS, FTIR, XRD, SEM-EDS, BET", "Evidence status": "Future phase"},
    {"Area": "Hybrid", "Technical detail": "Biofilter → photocatalytic; photocatalytic → biofilter; parallel configuration", "Evidence status": "Future phase"},
])

st.title("📊 H₂S Research Analysis Suite")
st.caption("PhD-specific analysis environment: H₂S biofilter performance, microbial screening, sulfur transformation, kinetics, statistics, stability, controls, publication figures and TEA/LCA-ready outputs.")
st.info("Research integrity rule: Actual uploaded measurements, reported PR values, preliminary observations, illustrative values and planned conditions are kept distinct. Do not use a reported summary value as a replicate-level dataset.")

# -----------------------------------------------------------------------------
# Research context / knowledge base
# -----------------------------------------------------------------------------
st.sidebar.header("Research workspace")
mode = st.sidebar.radio("Choose analysis", [
    "🧭 Research Knowledge Base",
    "📥 Upload & Analyze Dataset",
    "🧫 Isolate & Biochemical Screening",
    "📈 Growth Curve",
    "🧪 H₂S Reactor Performance",
    "🔬 Sulfur Transformation",
    "🧮 Kinetics & Regression",
    "🧬 Controls & Biological Attribution",
    "📊 Advanced Statistics",
    "🧱 Biofilm / Support Material",
    "🖼️ Publication Figures",
    "🧾 Data Quality & Reporting",
])

if mode == "🧭 Research Knowledge Base":
    st.header("🧭 Your PhD research context")
    c = st.columns(4)
    c[0].metric("Model pollutant", "H₂S")
    c[1].metric("Isolates screened", "9")
    c[2].metric("Selected isolate", "I-Tn2")
    c[3].metric("Column volume", "~0.589 L")

    st.subheader("Research objectives")
    for i, item in enumerate(RESEARCH_PROFILE["objectives"], 1):
        st.markdown(f"**{i}.** {item}")

    tab1, tab2, tab3, tab4 = st.tabs(["Reported results", "Methods", "Biochemistry", "Experimental roadmap"])
    with tab1:
        st.dataframe(REPORTED_RESULTS, width="stretch", hide_index=True)
        st.warning("These are previously reported/summary values. They are not substituted for raw replicate observations when inferential statistics are calculated.")
    with tab2:
        st.dataframe(METHODS_PROFILE, width="stretch", hide_index=True)
    with tab3:
        st.dataframe(BIOCHEMICAL_PROFILE, width="stretch", hide_index=True)
    with tab4:
        roadmap = pd.DataFrame([
            {"Phase": 1, "Component": "SOB/process optimization", "Status": "Completed + ongoing", "Key outputs": "Isolation, screening, medium optimization, operating conditions"},
            {"Phase": 2, "Component": "Biological biofilter", "Status": "Active", "Key outputs": "Clay-bead biofilm, EBRT, loading, pH, stability"},
            {"Phase": 3, "Component": "Photocatalytic reactor", "Status": "Upcoming", "Key outputs": "Catalyst, light, residence time, kinetics"},
            {"Phase": 4, "Component": "Hybrid system", "Status": "Upcoming", "Key outputs": "Series/parallel comparison, resilience"},
            {"Phase": 5, "Component": "TEA + scale-up", "Status": "Upcoming", "Key outputs": "Energy, cost, NPV, IRR, payback, scale-up"},
        ])
        st.dataframe(roadmap, width="stretch", hide_index=True)

    st.subheader("Core equations")
    equations = pd.DataFrame([
        {"Metric": "Removal efficiency", "Equation": "RE = (Cin − Cout) / Cin × 100"},
        {"Metric": "EBRT", "Equation": "EBRT = Vb / Q"},
        {"Metric": "Inlet loading", "Equation": "IL = Q × Cin / Vb"},
        {"Metric": "Elimination capacity", "Equation": "EC = Q × (Cin − Cout) / Vb"},
        {"Metric": "Sulfur pathway", "Equation": "H₂S(g) → H₂S(aq)/HS⁻ → S⁰ → SO₄²⁻ (proposed until measured)"},
    ])
    st.dataframe(equations, width="stretch", hide_index=True)
    st.caption("Use the actual bed-volume definition consistently. Geometric column volume (~0.589 L) is not automatically equivalent to packed-bed/empty-bed volume.")
    st.stop()

# -----------------------------------------------------------------------------
# Shared upload helper
# -----------------------------------------------------------------------------
def read_uploaded(uploaded):
    if uploaded is None:
        return None
    try:
        return pd.read_csv(uploaded) if uploaded.name.lower().endswith(".csv") else pd.read_excel(uploaded)
    except Exception as exc:
        st.error(f"Could not read the file: {exc}")
        return None

# -----------------------------------------------------------------------------
# Isolate / biochemical screening
# -----------------------------------------------------------------------------
if mode == "🧫 Isolate & Biochemical Screening":
    st.header("🧫 Isolate screening & biochemical characterization")
    st.caption("Designed around the nine-isolate screening workflow and I-Tn2 selection.")
    uploaded = st.file_uploader("Upload isolate-screening Excel/CSV (optional)", type=["xlsx", "csv"], key="isolate_upload")
    df = read_uploaded(uploaded)
    if df is None:
        st.subheader("Known screening context")
        st.dataframe(BIOCHEMICAL_PROFILE, width="stretch", hide_index=True)
        st.markdown("### Recommended isolate dataset")
        st.dataframe(pd.DataFrame([
            {"Isolate":"I-Tn1","OD600":0.0,"pH_final":7.0,"Sulfate_mg_L":np.nan,"CFU_mL":np.nan,"Protein_mg_mL":np.nan,"Gram":""},
            {"Isolate":"I-Tn2","OD600":1.0,"pH_final":2.5,"Sulfate_mg_L":np.nan,"CFU_mL":np.nan,"Protein_mg_mL":np.nan,"Gram":""},
            {"Isolate":"I-Tn3","OD600":np.nan,"pH_final":np.nan,"Sulfate_mg_L":np.nan,"CFU_mL":np.nan,"Protein_mg_mL":np.nan,"Gram":""},
        ]), width="stretch", hide_index=True)
        st.info("Upload your organized isolate workbook to calculate rankings, normalized scores, correlation heatmaps and publication figures.")
        st.stop()
    st.success(f"Loaded {len(df):,} rows × {len(df.columns):,} columns")
    st.dataframe(df, width="stretch")
    numeric = df.select_dtypes(include=np.number).columns.tolist()
    id_candidates = [c for c in df.columns if df[c].nunique(dropna=True) <= max(20, len(df))]
    if numeric:
        isolate_col = st.selectbox("Isolate identifier", id_candidates or list(df.columns), key="iso_id")
        selected_metrics = st.multiselect("Screening metrics", numeric, default=numeric[:min(5, len(numeric))])
        if selected_metrics:
            mat = df[[isolate_col] + selected_metrics].copy()
            for col in selected_metrics:
                mat[col] = pd.to_numeric(mat[col], errors="coerce")
            st.subheader("Screening table")
            st.dataframe(mat, width="stretch")
            z = mat[selected_metrics].copy()
            for col in selected_metrics:
                sd = z[col].std(skipna=True)
                z[col] = (z[col] - z[col].mean()) / sd if sd and np.isfinite(sd) else 0
            z.index = mat[isolate_col].astype(str)
            st.subheader("Standardized screening heatmap")
            st.plotly_chart(px.imshow(z.T, aspect="auto", color_continuous_midpoint=0, title="Standardized isolate-performance profile"), width="stretch")
            direction = st.multiselect("Metrics where higher is preferred", selected_metrics, default=selected_metrics)
            score = pd.Series(0.0, index=mat.index)
            for col in selected_metrics:
                v = mat[col]
                rng = v.max() - v.min()
                norm = (v-v.min())/rng if rng and np.isfinite(rng) else pd.Series(0.0,index=v.index)
                if col not in direction:
                    norm = 1-norm
                score += norm.fillna(0)
            out = mat[[isolate_col]].copy(); out["Composite_score"] = score; out = out.sort_values("Composite_score", ascending=False)
            st.subheader("Composite screening ranking")
            st.dataframe(out, width="stretch", hide_index=True)
            st.download_button("⬇️ Download isolate ranking", out.to_csv(index=False).encode("utf-8"), "isolate_screening_ranking.csv", "text/csv")
    st.stop()

# -----------------------------------------------------------------------------
# Growth curve
# -----------------------------------------------------------------------------
if mode == "📈 Growth Curve":
    st.header("📈 Growth curve & growth-phase analysis")
    st.caption("Growth interpretation is deliberately conservative: OD decline alone is not labelled as cell death, and the maximum-biomass/transition period is not automatically called stationary phase.")
    uploaded = st.file_uploader("Upload growth-curve Excel/CSV", type=["xlsx", "csv"], key="growth_upload")
    df = read_uploaded(uploaded)
    if df is None:
        st.info("Upload your I-Tn2 OD₆₀₀ time-series. Previously reported context: rapid biomass development was observed roughly in the 32–78 h region, with a reported maximum near OD₆₀₀ ≈ 1.0; later interpretation should follow the actual uploaded measurements.")
        st.dataframe(pd.DataFrame([
            {"Time_h":0,"OD600":np.nan,"Data_status":"Actual/illustrative flag required"},
            {"Time_h":32,"OD600":np.nan,"Data_status":"Actual/illustrative flag required"},
            {"Time_h":78,"OD600":1.0,"Data_status":"Reported summary; not raw replicate data"},
            {"Time_h":88,"OD600":np.nan,"Data_status":"Workbook-specific value should be verified"},
            {"Time_h":180,"OD600":np.nan,"Data_status":"Actual/illustrative flag required"},
        ]), width="stretch", hide_index=True)
        st.stop()
    st.dataframe(df, width="stretch")
    nums=df.select_dtypes(include=np.number).columns.tolist()
    if len(nums)>=2:
        t=st.selectbox("Time", nums, key="g_time")
        y=st.selectbox("OD/biomass response", [c for c in nums if c!=t], key="g_y")
        status_cols=[c for c in df.columns if "status" in str(c).lower() or "actual" in str(c).lower() or "source" in str(c).lower()]
        if status_cols:
            sc=st.selectbox("Data-status column (optional)", ["None"]+status_cols, key="g_status")
            if sc!="None":
                keep=~df[sc].astype(str).str.lower().str.contains("illustrative|example|planned", regex=True)
                if not keep.all(): st.warning(f"Excluded {int((~keep).sum())} rows marked illustrative/example/planned from quantitative fitting.")
                df=df[keep].copy()
        d=df[[t,y]].apply(pd.to_numeric,errors="coerce").dropna().sort_values(t)
        st.plotly_chart(px.line(d,x=t,y=y,markers=True,title="Growth curve"),width="stretch")
        if len(d)>=4:
            st.subheader("Phase-aware trend")
            d["dOD_dt"]=np.gradient(d[y].to_numpy(), d[t].to_numpy())
            st.dataframe(d,width="stretch")
            peak=d.loc[d[y].idxmax()]
            c=st.columns(3); c[0].metric("Maximum observed OD",f"{peak[y]:.4g}"); c[1].metric("Time at maximum",f"{peak[t]:.4g}"); c[2].metric("Points",str(len(d)))
            st.warning("Do not call the descending OD region 'cell death' without viability evidence. Treat it as a decline in measured optical density.")
    st.stop()

# -----------------------------------------------------------------------------
# H2S reactor performance
# -----------------------------------------------------------------------------
if mode == "🧪 H₂S Reactor Performance":
    st.header("🧪 H₂S biofilter performance")
    st.caption("Removal efficiency, EBRT, inlet loading and elimination capacity with consistent reactor-volume definitions.")
    uploaded = st.file_uploader("Upload reactor-performance Excel/CSV", type=["xlsx", "csv"], key="reactor_upload")
    df=read_uploaded(uploaded)
    if df is None:
        st.subheader("Previously reported operating envelope")
        c=st.columns(5)
        c[0].metric("Column", "300 × 50 mm")
        c[1].metric("Geometric volume", "~0.589 L")
        c[2].metric("EBRT range", "20–80 s")
        c[3].metric("H₂S loading", "~5–25 g/m³·h")
        c[4].metric("Selected isolate", "I-Tn2")
        st.dataframe(REPORTED_RESULTS, width="stretch", hide_index=True)
        st.info("Upload the actual inlet/outlet/flow dataset to calculate EC and loading. Do not assume the geometric 0.589 L is the empty-bed volume.")
        st.stop()
    st.dataframe(df,width="stretch")
    nums=df.select_dtypes(include=np.number).columns.tolist()
    def pick(label, keywords, exclude=None):
        cand=[c for c in nums if any(k in str(c).lower() for k in keywords) and c!=exclude]
        return st.selectbox(label,cand or nums,key=label)
    if len(nums)>=2:
        cin_col=pick("Inlet H₂S",["cin","inlet","input","h2s_in"])
        cout_col=pick("Outlet H₂S",["cout","outlet","output","h2s_out"],cin_col)
        flow_cand=[c for c in nums if any(k in str(c).lower() for k in ["flow","q","lpm","l/min"]) and c not in [cin_col,cout_col]]
        flow_col=st.selectbox("Gas flow (numeric, consistent unit)",flow_cand or ["None"],key="flow")
        vol_default=RESEARCH_PROFILE["geometric_volume_L"]
        vol=st.number_input("Bed/empty-bed volume used for calculation (L)",min_value=1e-9,value=float(vol_default),help="Explicitly state whether this is geometric, packed-bed or empty-bed volume.")
        volume_basis=st.selectbox("Volume basis",["Geometric column volume","Empty-bed volume","Packed-bed/gas void volume","Other explicitly defined basis"])
        x=df[[cin_col,cout_col]].apply(pd.to_numeric,errors="coerce")
        df["RE_%"]=(x[cin_col]-x[cout_col])/x[cin_col]*100
        if flow_col!="None":
            q=df[flow_col].astype(float)
            # Assume L/min and convert to m3/h if column label suggests L/min.
            if any(k in str(flow_col).lower() for k in ["lpm","l/min","l min"]):
                q_m3_h=q*0.06
            else:
                q_m3_h=q
            cin=x[cin_col]
            # ppm to g/m3 H2S at ~25 C, 1 atm: 1 ppm ≈ 1.394 mg/m3.
            ppm_to_g_m3=0.001394
            cin_g_m3=cin*ppm_to_g_m3
            df["Inlet_loading_g_m3_h"]=q_m3_h*cin_g_m3/vol
            df["Elimination_capacity_g_m3_h"]=q_m3_h*(cin_g_m3-(x[cout_col]*ppm_to_g_m3))/vol
            df["EBRT_s"]=(vol/(q_m3_h/60))*1.0
        st.subheader("Calculated reactor metrics")
        st.dataframe(df,width="stretch")
        c=st.columns(4); c[0].metric("Mean RE",f"{df['RE_%'].mean():.2f}%"); c[1].metric("Minimum RE",f"{df['RE_%'].min():.2f}%");
        if "Elimination_capacity_g_m3_h" in df: c[2].metric("Mean EC",f"{df['Elimination_capacity_g_m3_h'].mean():.3g} g/m³·h")
        if "EBRT_s" in df: c[3].metric("Mean calculated EBRT",f"{df['EBRT_s'].mean():.3g} s")
        st.caption(f"Calculation volume basis: {volume_basis}. State this explicitly in your thesis/PR because geometric volume, empty-bed volume and gas void volume are not interchangeable.")
        if "EBRT_s" in df:
            st.plotly_chart(px.scatter(df,x="EBRT_s",y="RE_%",trendline="ols",title="H₂S removal vs calculated EBRT"),width="stretch")
        if "Inlet_loading_g_m3_h" in df:
            st.plotly_chart(px.scatter(df,x="Inlet_loading_g_m3_h",y="RE_%",trendline="ols",title="H₂S removal vs inlet loading"),width="stretch")
        st.download_button("⬇️ Download reactor calculations",df.to_csv(index=False).encode("utf-8"),"h2s_reactor_metrics.csv","text/csv")
    st.stop()

# -----------------------------------------------------------------------------
# Sulfur transformation and mass balance
# -----------------------------------------------------------------------------
if mode == "🔬 Sulfur Transformation":
    st.header("🔬 Sulfur transformation & mass balance")
    st.caption("Removal is not automatically biodegradation. This module links gas-phase removal to dissolved sulfide, sulfate and elemental sulfur evidence.")
    uploaded=st.file_uploader("Upload sulfur-analysis dataset (optional)",type=["xlsx","csv"],key="sulfur_upload")
    df=read_uploaded(uploaded)
    if df is None:
        st.dataframe(pd.DataFrame([
            {"Pool":"Gas H₂S","Initial":100,"Final":6,"Unit":"ppm","Interpretation":"Gas-phase removal"},
            {"Pool":"Dissolved sulfide","Initial":50,"Final":8,"Unit":"mg/L","Interpretation":"Intermediate sulfur pool"},
            {"Pool":"Sulfate","Initial":65,"Final":285,"Unit":"mg/L","Interpretation":"Possible oxidation product"},
            {"Pool":"Elemental sulfur","Initial":np.nan,"Final":np.nan,"Unit":"mg/L or mg","Interpretation":"Measure separately where possible"},
        ]),width="stretch",hide_index=True)
        st.warning("The displayed values are previously reported summary observations. A true sulfur mass balance requires compatible units, sampling volumes/flows and all relevant sulfur pools.")
        st.stop()
    st.dataframe(df,width="stretch")
    nums=df.select_dtypes(include=np.number).columns.tolist()
    if len(nums)>=2:
        a=st.selectbox("Initial/condition A",nums,key="s_a"); b=st.selectbox("Final/condition B",[c for c in nums if c!=a],key="s_b")
        work=df[[a,b]].apply(pd.to_numeric,errors="coerce")
        work["Absolute_change"]=work[b]-work[a]
        work["Percent_change"]=work["Absolute_change"]/work[a].abs()*100
        st.dataframe(work,width="stretch")
        st.info("For publication, convert all sulfur pools to a common mass basis before claiming closure. Account for gas flow, sampling volume, liquid volume, packing-associated sulfur and analytical recovery.")
    st.stop()

# -----------------------------------------------------------------------------
# Kinetics
# -----------------------------------------------------------------------------
if mode == "🧮 Kinetics & Regression":
    st.header("🧮 H₂S kinetics & regression")
    st.caption("Fit multiple candidate models and compare R², RMSE and physical plausibility. Do not select a kinetic order in advance.")
    uploaded=st.file_uploader("Upload concentration-vs-time data",type=["xlsx","csv"],key="kin_upload")
    df=read_uploaded(uploaded)
    if df is None:
        st.markdown("### Candidate models")
        st.latex(r"C_t=C_0-kt")
        st.latex(r"\ln(C_t)=\ln(C_0)-kt")
        st.latex(r"1/C_t=1/C_0+kt")
        st.markdown("**Additional packed-bed models:** Ottengraf and Langmuir–Hinshelwood should be used only when the dataset and mechanistic assumptions support them.")
        st.info("Upload measured H₂S concentration/time observations to perform the fit.")
        st.stop()
    nums=df.select_dtypes(include=np.number).columns.tolist()
    if len(nums)>=2:
        t=st.selectbox("Time",nums,key="k_t"); c=st.selectbox("H₂S concentration",[x for x in nums if x!=t],key="k_c")
        d=df[[t,c]].apply(pd.to_numeric,errors="coerce").dropna().sort_values(t)
        d=d[d[c]>0]
        if len(d)>=3:
            x=d[t].to_numpy(float); y=d[c].to_numpy(float)
            fits=[]
            # zero order
            z=stats.linregress(x,y); pred=z.intercept+z.slope*x; fits.append({"Model":"Zero-order","k":-z.slope,"R²":z.rvalue**2,"RMSE":np.sqrt(np.mean((y-pred)**2))})
            # first order
            z=stats.linregress(x,np.log(y)); pred=np.exp(z.intercept+z.slope*x); fits.append({"Model":"First-order","k":-z.slope,"R²":z.rvalue**2,"RMSE":np.sqrt(np.mean((y-pred)**2))})
            # second order
            z=stats.linregress(x,1/y); inv_pred=z.intercept+z.slope*x; pred=1/inv_pred; valid=np.isfinite(pred)&(inv_pred!=0); fits.append({"Model":"Second-order","k":z.slope,"R²":z.rvalue**2,"RMSE":np.sqrt(np.mean((y[valid]-pred[valid])**2))})
            result=pd.DataFrame(fits).sort_values("RMSE")
            st.dataframe(result,width="stretch",hide_index=True)
            best=result.iloc[0]["Model"]
            st.success(f"Best numerical fit by RMSE: {best}. Confirm physical plausibility and experimental assumptions before reporting it as the governing kinetic model.")
            # show linearized fits
            fig=go.Figure()
            fig.add_trace(go.Scatter(x=x,y=y,mode="markers",name="Observed"))
            for row in result.itertuples():
                if row.Model=="Zero-order":
                    zz=stats.linregress(x,y); yp=zz.intercept+zz.slope*x
                elif row.Model=="First-order":
                    zz=stats.linregress(x,np.log(y)); yp=np.exp(zz.intercept+zz.slope*x)
                else:
                    zz=stats.linregress(x,1/y); inv=zz.intercept+zz.slope*x; yp=np.where(inv>0,1/inv,np.nan)
                fig.add_trace(go.Scatter(x=x,y=yp,mode="lines",name=row.Model))
            st.plotly_chart(fig,width="stretch")
            st.download_button("⬇️ Download kinetic comparison",result.to_csv(index=False).encode("utf-8"),"h2s_kinetic_model_comparison.csv","text/csv")
    st.stop()

# -----------------------------------------------------------------------------
# Biological vs abiotic controls
# -----------------------------------------------------------------------------
if mode == "🧬 Controls & Biological Attribution":
    st.header("🧬 Biological vs abiotic attribution")
    st.caption("A gas-phase concentration decrease alone does not prove biodegradation. Compare inoculated and uninoculated systems under comparable conditions.")
    uploaded=st.file_uploader("Upload control-comparison dataset (optional)",type=["xlsx","csv"],key="control_upload")
    df=read_uploaded(uploaded)
    if df is None:
        df=pd.DataFrame([
            {"System":"Inoculated clay-bead biofilter","Cin_ppm":100,"Cout_ppm":6,"Removal_%":94,"Dissolved_sulfide_initial_mg_L":50,"Dissolved_sulfide_final_mg_L":8,"Sulfate_initial_mg_L":65,"Sulfate_final_mg_L":285,"pH_initial":7.5,"pH_final":2.5,"Status":"Reported PR summary"},
            {"System":"Uninoculated clay-bead control","Cin_ppm":100,"Cout_ppm":72,"Removal_%":28,"Dissolved_sulfide_initial_mg_L":np.nan,"Dissolved_sulfide_final_mg_L":np.nan,"Sulfate_initial_mg_L":np.nan,"Sulfate_final_mg_L":np.nan,"pH_initial":np.nan,"pH_final":np.nan,"Status":"Reported PR summary"},
        ])
    else:
        st.dataframe(df,width="stretch")
        nums=df.select_dtypes(include=np.number).columns.tolist()
        if len(nums)>=2:
            cin=st.selectbox("Inlet H₂S",nums,key="c_cin"); cout=st.selectbox("Outlet H₂S",[x for x in nums if x!=cin],key="c_cout")
            df["Calculated_RE_%"]=(df[cin]-df[cout])/df[cin]*100
    st.dataframe(df,width="stretch",hide_index=True)
    if {"Cin_ppm","Cout_ppm"}.issubset(df.columns):
        df["Calculated_RE_%"]=(df.Cin_ppm-df.Cout_ppm)/df.Cin_ppm*100
        st.bar_chart(df.set_index("System")["Calculated_RE_%"])
        if len(df)>=2:
            st.info("The inoculated-vs-uninoculated contrast is stronger evidence when flow, EBRT, inlet concentration, packing, moisture and sampling conditions are matched.")
    st.subheader("Evidence chain")
    for item in [
        "Gas-phase H₂S decreases between inlet and outlet.",
        "Uninoculated/blank removal is quantified under comparable conditions.",
        "Dissolved sulfide, sulfate and/or elemental sulfur are measured.",
        "Microbial colonization/activity is independently demonstrated.",
        "A sulfur mass balance is attempted with compatible units.",
    ]:
        st.checkbox(item, key="ev_"+str(abs(hash(item))))
    st.stop()

# -----------------------------------------------------------------------------
# Biofilm / support material
# -----------------------------------------------------------------------------
if mode == "🧱 Biofilm / Support Material":
    st.header("🧱 Biofilm & support-material analysis")
    st.caption("Tracks the evidence-driven transition from glass beads to clay beads and keeps surface-property claims separate from measured biofilm evidence.")
    st.dataframe(pd.DataFrame([
        {"Support":"Glass beads","Observed issue":"Inadequate biofilm establishment under tested conditions","Decision":"Replaced for subsequent campaign"},
        {"Support":"Clay beads","Role":"Selected support for subsequent biofilter experiments","Evidence to collect":"Colonization images, biomass/attachment, SEM/microscopy where available"},
        {"Support":"Clay + fly ash","Role":"Candidate comparison","Evidence to collect":"Attachment, pressure drop, moisture retention, RE/EC and stability"},
    ]),width="stretch",hide_index=True)
    uploaded=st.file_uploader("Upload support-comparison dataset (optional)",type=["xlsx","csv"],key="support_upload")
    df=read_uploaded(uploaded)
    if df is not None:
        st.dataframe(df,width="stretch")
        nums=df.select_dtypes(include=np.number).columns.tolist()
        groups=[c for c in df.columns if df[c].nunique(dropna=True)<=10]
        if nums and groups:
            g=st.selectbox("Support/material",groups,key="sup_g"); y=st.selectbox("Response",nums,key="sup_y")
            st.plotly_chart(px.box(df,x=g,y=y,points="all",title=f"{y} by support material"),width="stretch")
    st.warning("Do not claim that clay improved biofilm solely from theoretical roughness/porosity. Link the material change to direct colonization, biomass and reactor-performance evidence.")
    st.stop()

# -----------------------------------------------------------------------------
# Publication figures
# -----------------------------------------------------------------------------
if mode == "🖼️ Publication Figures":
    st.header("🖼️ Publication / PR figure builder")
    uploaded=st.file_uploader("Upload any analysis dataset",type=["xlsx","csv"],key="fig_upload")
    df=read_uploaded(uploaded)
    if df is None:
        st.info("Upload a dataset to create a figure. The figure templates below match your PR structure: removal vs EBRT, removal vs loading, daily stability, biological vs abiotic and pH/sulfur trends.")
        st.stop()
    st.dataframe(df,width="stretch")
    nums=df.select_dtypes(include=np.number).columns.tolist(); cats=[c for c in df.columns if df[c].nunique(dropna=True)<=30]
    if nums:
        chart=st.selectbox("Figure type",["Scatter + trendline","Line","Box + individual points","Bar"],key="fig_type")
        x=st.selectbox("X variable",nums,key="fig_x")
        y=st.selectbox("Y variable",[c for c in nums if c!=x] or nums,key="fig_y")
        color=st.selectbox("Grouping (optional)",["None"]+cats,key="fig_group")
        kwargs={} if color=="None" else {"color":color}
        if chart=="Scatter + trendline": fig=px.scatter(df,x=x,y=y,trendline="ols",**kwargs)
        elif chart=="Line": fig=px.line(df,x=x,y=y,markers=True,**kwargs)
        elif chart=="Box + individual points": fig=px.box(df,x=x,y=y,points="all",**kwargs)
        else: fig=px.bar(df,x=x,y=y,**kwargs)
        fig.update_layout(template="plotly_white",font=dict(size=14),margin=dict(l=60,r=30,t=60,b=60))
        st.plotly_chart(fig,width="stretch")
        st.download_button("⬇️ Export figure specification",str(fig.to_dict()).encode("utf-8"),"figure_spec.txt","text/plain")
    st.stop()

# -----------------------------------------------------------------------------
# Data quality / reporting
# -----------------------------------------------------------------------------
if mode == "🧾 Data Quality & Reporting":
    st.header("🧾 Data quality, provenance & reporting")
    uploaded=st.file_uploader("Upload dataset",type=["xlsx","csv"],key="dq_upload")
    df=read_uploaded(uploaded)
    if df is None:
        st.subheader("Research-specific data-quality rules")
        rules=pd.DataFrame([
            {"Check":"Independent replicate IDs","Requirement":"Required for biological inference","Risk if missing":"Pseudoreplication"},
            {"Check":"Technical replicates","Requirement":"Collapse/average within independent replicate before inferential testing","Risk if ignored":"Artificially inflated n"},
            {"Check":"Actual vs illustrative values","Requirement":"Flag provenance","Risk if ignored":"False precision"},
            {"Check":"EBRT basis","Requirement":"Define Vb explicitly","Risk if ignored":"Incorrect loading/EC"},
            {"Check":"H₂S calibration","Requirement":"Record calibration/range/uncertainty","Risk if ignored":"Systematic bias"},
            {"Check":"Biological control","Requirement":"Uninoculated/blank comparison","Risk if missing":"Weak biological attribution"},
            {"Check":"Sulfur balance","Requirement":"Compatible units and sampling basis","Risk if missing":"Cannot establish transformation/closure"},
            {"Check":"Stability","Requirement":"Report time trend, not only maximum RE","Risk if missing":"Overstates performance"},
        ])
        st.dataframe(rules,width="stretch",hide_index=True)
        st.stop()
    c=st.columns(5)
    c[0].metric("Rows",len(df)); c[1].metric("Columns",len(df.columns)); c[2].metric("Missing cells",int(df.isna().sum().sum())); c[3].metric("Duplicate rows",int(df.duplicated().sum())); c[4].metric("Numeric variables",len(df.select_dtypes(include=np.number).columns))
    st.dataframe(df.head(100),width="stretch")
    missing=df.isna().sum().sort_values(ascending=False).reset_index(); missing.columns=["Variable","Missing"]
    st.subheader("Missingness")
    st.dataframe(missing[missing.Missing>0],width="stretch",hide_index=True)
    st.subheader("Reporting checklist")
    for item in [
        "Experimental unit is explicitly defined.",
        "Biological/independent and technical replicates are distinguished.",
        "n is reported for every statistical comparison.",
        "Mean ± SD/SEM is used consistently and defined.",
        "Raw inlet/outlet H₂S and operating conditions are retained.",
        "EBRT volume basis and gas-flow units are explicit.",
        "Calibration and measurement uncertainty are documented.",
        "Abiotic/blank controls are reported.",
        "Sulfur-product measurements are linked to mass balance where possible.",
        "Statistical test, effect size and confidence interval are reported.",
        "Figures distinguish measured data from model fits.",
    ]:
        st.checkbox(item)
    st.stop()

# -----------------------------------------------------------------------------
# Upload & analyze / advanced statistics
# -----------------------------------------------------------------------------
if mode in ["📥 Upload & Analyze Dataset","📊 Advanced Statistics"]:
    st.header("📊 Advanced Experimental Data Analysis")
    st.caption("Replicate-aware statistics, time-series analysis, regression, effect sizes, uncertainty and publication-oriented visualization.")
    uploaded=st.file_uploader("Upload Excel or CSV dataset",type=["xlsx","csv"],key="adv_upload")
    df=read_uploaded(uploaded)
    if df is None:
        st.markdown("### Recommended long-format structure")
        st.dataframe(pd.DataFrame([
            {"Group":"Control","BiologicalReplicate":"B1","TechnicalReplicate":"T1","Time":0,"Value":10.0},
            {"Group":"Control","BiologicalReplicate":"B1","TechnicalReplicate":"T2","Time":0,"Value":10.5},
            {"Group":"Treatment","BiologicalReplicate":"B1","TechnicalReplicate":"T1","Time":0,"Value":8.0},
            {"Group":"Treatment","BiologicalReplicate":"B1","TechnicalReplicate":"T2","Time":0,"Value":8.4},
        ]),width="stretch",hide_index=True)
        st.info("For your H₂S work, useful columns include time/day, inlet H₂S, outlet H₂S, group/condition, biological replicate, technical replicate, pH, sulfate, dissolved sulfide, flow, EBRT and loading.")
        st.stop()

    st.success(f"Loaded {len(df):,} rows × {len(df.columns):,} columns")
    numeric_cols=df.select_dtypes(include=np.number).columns.tolist()
    if not numeric_cols: st.error("No numeric variables detected."); st.stop()
    with st.expander("Data quality snapshot",expanded=True):
        c=st.columns(4); c[0].metric("Rows",len(df)); c[1].metric("Columns",len(df.columns)); c[2].metric("Missing",int(df.isna().sum().sum())); c[3].metric("Duplicates",int(df.duplicated().sum()))
        st.dataframe(df.head(100),width="stretch")

    value_col=st.sidebar.selectbox("Measurement / response",numeric_cols,key="a_value")
    other=[c for c in numeric_cols if c!=value_col]
    time_candidates=[c for c in df.columns if c!=value_col and any(k in str(c).lower() for k in ["time","day","hour","ebrt","loading"])]
    time_col=st.sidebar.selectbox("Time / condition axis",["None"]+time_candidates+other,key="a_time")
    time_col=None if time_col=="None" else time_col
    group_candidates=[c for c in df.columns if c!=value_col and df[c].nunique(dropna=True)<=30]
    group_col=st.sidebar.selectbox("Experimental group",["None"]+group_candidates,key="a_group")
    group_col=None if group_col=="None" else group_col
    rep_candidates=[c for c in df.columns if any(k in str(c).lower() for k in ["biological","independent","replicate","sample","isolate"])]
    rep_col=st.sidebar.selectbox("Biological/independent replicate ID",["None"]+rep_candidates,key="a_rep")
    rep_col=None if rep_col=="None" else rep_col
    tech_candidates=[c for c in df.columns if any(k in str(c).lower() for k in ["technical","tech_rep","technicalrep"])]
    tech_col=st.sidebar.selectbox("Technical replicate ID",["None"]+tech_candidates,key="a_tech")
    tech_col=None if tech_col=="None" else tech_col

    work=df.copy(); work["__value"]=pd.to_numeric(work[value_col],errors="coerce"); work=work[np.isfinite(work.__value)].copy(); work["__group"]=work[group_col].astype(str) if group_col else "All observations"
    if time_col: work["__time"]=pd.to_numeric(work[time_col],errors="coerce")

    st.subheader("1. Descriptive statistics")
    summary=work.groupby("__group")["__value"].agg(n="count",mean="mean",SD="std",median="median",min="min",max="max").reset_index(); summary["SEM"]=work.groupby("__group")["__value"].sem().values; summary["CV_%"]=summary.SD.div(summary.mean.replace(0,np.nan)).abs()*100
    st.dataframe(summary,width="stretch",hide_index=True)

    st.subheader("2. Replicate-aware analysis")
    if rep_col:
        if tech_col:
            tech=work.groupby(["__group",rep_col,tech_col])["__value"].mean().reset_index(name="technical_mean")
            analysis_df=tech.groupby(["__group",rep_col])["technical_mean"].mean().reset_index(name="__value")
            st.caption("Technical replicates were collapsed within independent replicate before inferential testing.")
        else:
            analysis_df=work.groupby(["__group",rep_col])["__value"].mean().reset_index(name="__value")
        st.dataframe(analysis_df,width="stretch",hide_index=True)
    else:
        analysis_df=work.copy(); st.warning("No biological/independent replicate ID selected. Inferential tests may suffer from pseudoreplication.")

    st.subheader("3. Between-group inference")
    groups=[g["__value"].dropna().to_numpy() for _,g in analysis_df.groupby("__group") if len(g["__value"].dropna())]
    names=[str(k) for k,g in analysis_df.groupby("__group") if len(g["__value"].dropna())]
    def cohen_d(a,b):
        a=np.asarray(a,float); b=np.asarray(b,float); pooled=np.sqrt(((len(a)-1)*np.var(a,ddof=1)+(len(b)-1)*np.var(b,ddof=1))/(len(a)+len(b)-2)); return (a.mean()-b.mean())/pooled if pooled else np.nan
    if len(groups)==2:
        r=stats.ttest_ind(groups[0],groups[1],equal_var=False); d=cohen_d(groups[0],groups[1]); c=st.columns(4); c[0].metric("Welch t",f"{r.statistic:.5g}"); c[1].metric("p",f"{r.pvalue:.5g}"); c[2].metric("Cohen d",f"{d:.5g}" if np.isfinite(d) else "N/A"); c[3].metric("Conclusion","p < 0.05" if r.pvalue<0.05 else "p ≥ 0.05")
    elif len(groups)>=3:
        r=stats.f_oneway(*groups); c=st.columns(2); c[0].metric("ANOVA F",f"{r.statistic:.5g}"); c[1].metric("p",f"{r.pvalue:.5g}")
        try:
            tuk=stats.tukey_hsd(*groups); pairs=[]
            for i in range(len(groups)):
                for j in range(i+1,len(groups)): pairs.append({"Group 1":names[i],"Group 2":names[j],"Mean difference":groups[i].mean()-groups[j].mean(),"p-value":tuk.pvalue[i,j]})
            st.dataframe(pd.DataFrame(pairs),width="stretch",hide_index=True)
        except Exception as exc: st.warning(f"Tukey HSD unavailable: {exc}")
    else: st.info("Need at least two independent groups for between-group inference.")

    st.subheader("4. Correlation / regression")
    if other:
        predictor=st.selectbox("Predictor",other,key="a_pred")
        xy=pd.DataFrame({"x":pd.to_numeric(df[predictor],errors="coerce"),"y":pd.to_numeric(df[value_col],errors="coerce")}).dropna()
        if len(xy)>=3:
            pear=stats.pearsonr(xy.x,xy.y); spear=stats.spearmanr(xy.x,xy.y); fit=stats.linregress(xy.x,xy.y); ci=stats.t.interval(.95,len(xy)-2,loc=fit.slope,scale=fit.stderr)
            c=st.columns(5); c[0].metric("Pearson r",f"{pear.statistic:.4g}"); c[1].metric("Pearson p",f"{pear.pvalue:.4g}"); c[2].metric("Spearman ρ",f"{spear.statistic:.4g}"); c[3].metric("R²",f"{fit.rvalue**2:.4g}"); c[4].metric("Slope 95% CI",f"{ci[0]:.4g}–{ci[1]:.4g}")
            st.plotly_chart(px.scatter(xy,x="x",y="y",trendline="ols",title=f"{value_col} vs {predictor}"),width="stretch")

    st.subheader("5. Time-series")
    if time_col:
        ts=work.dropna(subset=["__time"]); plot_df=ts.groupby(["__group","__time"])["__value"].agg(mean="mean",SD="std",n="count").reset_index(); plot_df["SEM"]=plot_df.SD/np.sqrt(plot_df.n)
        st.plotly_chart(px.line(plot_df,x="__time",y="mean",color="__group",markers=True,error_y="SEM",title=f"{value_col} over time (mean ± SEM)"),width="stretch")
        st.dataframe(plot_df,width="stretch",hide_index=True)
        if rep_col: st.warning("If the same biological replicate is measured repeatedly over time, do not treat time points as independent. Use repeated-measures or mixed-effects methods as appropriate.")

    st.subheader("6. Publication-oriented boxplot")
    st.plotly_chart(px.box(work,x="__group",y="__value",points="all",title=f"{value_col}: distribution and individual observations"),width="stretch")

    st.subheader("7. Export")
    st.download_button("⬇️ Descriptive summary",summary.to_csv(index=False).encode("utf-8"),"advanced_descriptive_summary.csv","text/csv")
    st.download_button("⬇️ Clean working dataset",work.to_csv(index=False).encode("utf-8"),"analysis_working_dataset.csv","text/csv")
    st.caption("Statistical results are research aids. Verify independence, normality, variance structure, repeated-measures structure and disciplinary reporting requirements before publication.")
    st.stop()

# Fallback
st.info("Select a research analysis module from the sidebar.")
