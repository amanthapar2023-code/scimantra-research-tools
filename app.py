
import io, math, statistics
from typing import Optional

import numpy as np
import pandas as pd
import streamlit as st
from scipy import stats
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="SciMantra Research Tools",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
:root { --sm-blue:#1565c0; --sm-dark:#0b1f33; }
.block-container { max-width: 1400px; padding-top: 1.5rem; }
.hero {
    padding: 1.5rem 1.7rem; border-radius: 18px;
    background: linear-gradient(135deg,#e8f3ff,#f8fbff);
    border: 1px solid #d7e8fa; margin-bottom: 1rem;
}
.hero h1 { margin:0; color:#0b1f33; font-size:2.35rem; }
.hero p { margin:.4rem 0 0; color:#38536b; font-size:1.05rem; }
.tool-card {
    border:1px solid #e3eaf0; border-radius:14px; padding:1rem;
    background:white; min-height:120px;
}
.small {color:#607d8b; font-size:.9rem;}
.formula {background:#f7f9fb; padding:.7rem 1rem; border-radius:10px;
          border-left:4px solid #1565c0;}
footer {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
<h1>🔬 SciMantra Research Tools</h1>
<p>Calculate • Analyze • Visualize • Understand — practical tools for science, laboratory work and research.</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.title("SCIMantra")
st.sidebar.caption("Science • Research • Learning")
section = st.sidebar.radio("Choose a tool", [
    "🏠 Dashboard",
    "🧪 Laboratory Calculators",
    "📊 Statistics",
    "🌱 Environmental Biotechnology",
    "📈 Data Analyzer",
    "🔬 Research Tools",
])

def download_df(df, filename="scimantra_results.csv"):
    st.download_button("⬇️ Download CSV", df.to_csv(index=False).encode("utf-8"),
                       filename, "text/csv")

def safe_float(x):
    try:
        return float(x)
    except Exception:
        return None

# ---------------- Dashboard ----------------
if section == "🏠 Dashboard":
    st.subheader("Research tools in one place")
    cols = st.columns(3)
    cards = [
        ("🧪 Laboratory", "Molarity, dilution, CFU/mL, BOD, COD, biomass and growth calculations."),
        ("📊 Statistics", "Mean, SD, SEM, CV, t-test, ANOVA, correlation and regression."),
        ("🌱 Environment", "Removal efficiency, loading, EBRT and H₂S analysis."),
        ("📈 Data Analyzer", "Upload Excel/CSV files, summarize replicates and create interactive graphs."),
        ("🔬 Research", "Standard curves, experimental design and manuscript checklists."),
        ("📥 Outputs", "Download tables and publication-ready interactive figures."),
    ]
    for i, (title, desc) in enumerate(cards):
        with cols[i % 3]:
            st.markdown(f'<div class="tool-card"><h3>{title}</h3><p>{desc}</p></div>', unsafe_allow_html=True)
    st.info("Tip: start with Data Analyzer if you already have an Excel/CSV research dataset.")

# ---------------- Lab ----------------
elif section == "🧪 Laboratory Calculators":
    tool = st.selectbox("Calculator", [
        "Molarity",
        "Dilution (C₁V₁ = C₂V₂)",
        "% Solution",
        "Normality",
        "CFU/mL",
        "Biomass concentration",
        "Growth rate",
        "Specific growth rate",
        "BOD",
        "COD",
    ])
    if tool == "Molarity":
        st.subheader("Molarity Calculator")
        mass = st.number_input("Mass of solute (g)", min_value=0.0, value=1.0)
        mw = st.number_input("Molecular weight (g/mol)", min_value=0.000001, value=58.44)
        vol = st.number_input("Final volume (L)", min_value=0.000001, value=1.0)
        m = mass / mw / vol
        st.metric("Molarity", f"{m:.6g} mol/L")
        st.markdown(f'<div class="formula">M = mass ÷ molecular weight ÷ volume(L)</div>', unsafe_allow_html=True)

    elif tool == "Dilution (C₁V₁ = C₂V₂)":
        st.subheader("Dilution Calculator")
        c1 = st.number_input("C₁ (stock concentration)", min_value=0.0, value=100.0)
        c2 = st.number_input("C₂ (desired concentration)", min_value=0.000001, value=10.0)
        v2 = st.number_input("V₂ (final volume)", min_value=0.000001, value=100.0)
        v1 = c2 * v2 / c1 if c1 else 0
        diluent = v2 - v1
        st.metric("Stock volume V₁", f"{v1:.4g}")
        st.metric("Diluent volume", f"{diluent:.4g}")

    elif tool == "% Solution":
        st.subheader("Percentage Solution")
        mode = st.selectbox("Type", ["w/v (% g per 100 mL)", "w/w (% g per 100 g)", "v/v (% mL per 100 mL)"])
        amount = st.number_input("Solute amount", min_value=0.0, value=5.0)
        total = st.number_input("Total amount/volume", min_value=0.000001, value=100.0)
        pct = amount / total * 100
        st.metric("Percentage", f"{pct:.4g}%")
        st.caption(mode)

    elif tool == "Normality":
        st.subheader("Normality Calculator")
        molarity = st.number_input("Molarity (mol/L)", min_value=0.0, value=1.0)
        n_factor = st.number_input("n-factor / equivalent factor", min_value=0.000001, value=1.0)
        st.metric("Normality", f"{molarity*n_factor:.6g} N")

    elif tool == "CFU/mL":
        st.subheader("CFU/mL Calculator")
        colonies = st.number_input("Colonies counted", min_value=0.0, value=125.0)
        dilution = st.number_input("Dilution factor denominator (e.g. 10⁻⁵ → 100000)", min_value=1.0, value=100000.0)
        plated = st.number_input("Volume plated (mL)", min_value=0.000001, value=0.1)
        cfu = colonies * dilution / plated
        st.metric("CFU/mL", f"{cfu:.6g}")
        st.markdown('<div class="formula">CFU/mL = colonies × reciprocal dilution ÷ volume plated (mL)</div>', unsafe_allow_html=True)

    elif tool == "Biomass concentration":
        st.subheader("Biomass Concentration")
        dry_mass = st.number_input("Dry biomass (g)", min_value=0.0, value=1.0)
        volume = st.number_input("Culture volume (L)", min_value=0.000001, value=1.0)
        st.metric("Biomass", f"{dry_mass/volume:.6g} g/L")

    elif tool == "Growth rate":
        st.subheader("Average Growth Rate")
        x1 = st.number_input("Measurement 1", value=0.1)
        x2 = st.number_input("Measurement 2", value=0.8)
        t1 = st.number_input("Time 1", value=0.0)
        t2 = st.number_input("Time 2", value=10.0)
        rate = (x2-x1)/(t2-t1) if t2 != t1 else 0
        st.metric("Growth rate", f"{rate:.6g} units/time")

    elif tool == "Specific growth rate":
        st.subheader("Specific Growth Rate")
        x1 = st.number_input("X₁ (biomass/concentration)", min_value=0.000001, value=0.1)
        x2 = st.number_input("X₂", min_value=0.000001, value=0.8)
        dt = st.number_input("Δt", min_value=0.000001, value=10.0)
        mu = math.log(x2/x1)/dt
        st.metric("μ", f"{mu:.6g} time⁻¹")
        st.markdown('<div class="formula">μ = ln(X₂/X₁) ÷ Δt</div>', unsafe_allow_html=True)

    elif tool == "BOD":
        st.subheader("BOD Calculator")
        initial = st.number_input("Initial DO (mg/L)", value=8.0)
        final = st.number_input("Final DO (mg/L)", value=3.0)
        sample_vol = st.number_input("Sample volume (mL)", value=15.0, min_value=0.000001)
        bottle_vol = st.number_input("Bottle volume (mL)", value=300.0, min_value=0.000001)
        dilution_factor = bottle_vol / sample_vol
        bod = (initial-final) * dilution_factor
        st.metric("Approx. BOD₅", f"{bod:.6g} mg/L")
        st.caption("Use the appropriate standard-method correction for seed, dilution water and blanks when applicable.")

    elif tool == "COD":
        st.subheader("COD Calculator")
        a = st.number_input("Blank titration A (mL)", value=20.0)
        b = st.number_input("Sample titration B (mL)", value=12.0)
        normality = st.number_input("Titrant normality", value=0.1, min_value=0.000001)
        volume = st.number_input("Sample volume (mL)", value=10.0, min_value=0.000001)
        cod = (a-b)*normality*8000/volume
        st.metric("COD", f"{cod:.6g} mg/L")
        st.caption("Verify the reagent-specific equation and method used in your laboratory.")

# ---------------- Statistics ----------------
elif section == "📊 Statistics":
    tool = st.selectbox("Statistical tool", [
        "Descriptive statistics", "t-Test", "One-way ANOVA", "Correlation", "Linear regression"
    ])
    uploaded = st.file_uploader("Upload CSV/Excel (optional)", type=["csv","xlsx"])
    df = None
    if uploaded:
        df = pd.read_csv(uploaded) if uploaded.name.endswith(".csv") else pd.read_excel(uploaded)
        st.dataframe(df.head(20), use_container_width=True)

    if tool == "Descriptive statistics":
        if df is not None:
            numeric = df.select_dtypes(include=np.number)
            result = numeric.describe().T
            result["SEM"] = numeric.sem()
            result["CV_%"] = numeric.std(ddof=1)/numeric.mean()*100
            st.dataframe(result, use_container_width=True)
            download_df(result.reset_index().rename(columns={"index":"Variable"}), "descriptive_statistics.csv")
        else:
            vals = st.text_area("Enter values separated by commas", "1,2,3,4,5,6")
            try:
                x = np.array([float(v.strip()) for v in vals.split(",") if v.strip()])
                if len(x):
                    c1,c2,c3,c4 = st.columns(4)
                    c1.metric("Mean", f"{x.mean():.5g}")
                    c2.metric("SD", f"{x.std(ddof=1):.5g}" if len(x)>1 else "NA")
                    c3.metric("SEM", f"{stats.sem(x):.5g}" if len(x)>1 else "NA")
                    c4.metric("CV %", f"{x.std(ddof=1)/x.mean()*100:.5g}" if len(x)>1 and x.mean()!=0 else "NA")
            except Exception:
                st.error("Please enter numeric values.")

    elif tool == "t-Test":
        a = st.text_area("Group A", "1,2,3,4,5")
        b = st.text_area("Group B", "2,3,4,5,6")
        try:
            x = [float(v) for v in a.split(",") if v.strip()]
            y = [float(v) for v in b.split(",") if v.strip()]
            res = stats.ttest_ind(x,y,equal_var=False)
            st.metric("t statistic", f"{res.statistic:.6g}")
            st.metric("p-value", f"{res.pvalue:.6g}")
            st.caption("Welch's independent two-sample t-test.")
        except Exception: st.warning("Enter two comma-separated numeric groups.")

    elif tool == "One-way ANOVA":
        groups_text = st.text_area("Groups (one group per line)", "1,2,3\n2,3,4\n5,6,7")
        try:
            groups = [[float(v) for v in line.split(",") if v.strip()] for line in groups_text.splitlines() if line.strip()]
            res = stats.f_oneway(*groups)
            st.metric("F statistic", f"{res.statistic:.6g}")
            st.metric("p-value", f"{res.pvalue:.6g}")
            st.caption("ANOVA tests whether at least one group mean differs; post-hoc tests may be needed.")
        except Exception: st.warning("Enter numeric groups, one group per line.")

    elif tool == "Correlation":
        x = st.text_area("X values", "1,2,3,4,5")
        y = st.text_area("Y values", "2,4,5,8,10")
        method = st.selectbox("Method", ["Pearson", "Spearman"])
        try:
            xx=np.array([float(v) for v in x.split(",") if v.strip()])
            yy=np.array([float(v) for v in y.split(",") if v.strip()])
            res = stats.pearsonr(xx,yy) if method=="Pearson" else stats.spearmanr(xx,yy)
            st.metric("Correlation coefficient", f"{res.statistic:.6g}")
            st.metric("p-value", f"{res.pvalue:.6g}")
        except Exception: st.warning("Enter equal-length numeric arrays.")

    elif tool == "Linear regression":
        x = st.text_area("X values", "1,2,3,4,5")
        y = st.text_area("Y values", "2,4,5,8,10")
        try:
            xx=np.array([float(v) for v in x.split(",") if v.strip()])
            yy=np.array([float(v) for v in y.split(",") if v.strip()])
            r=stats.linregress(xx,yy)
            r2=r.rvalue**2
            c1,c2,c3,c4=st.columns(4)
            c1.metric("Slope", f"{r.slope:.6g}")
            c2.metric("Intercept", f"{r.intercept:.6g}")
            c3.metric("R²", f"{r2:.6g}")
            c4.metric("p-value", f"{r.pvalue:.6g}")
            fig=go.Figure()
            fig.add_trace(go.Scatter(x=xx,y=yy,mode="markers",name="Data"))
            order=np.argsort(xx)
            fig.add_trace(go.Scatter(x=xx[order],y=r.intercept+r.slope*xx[order],mode="lines",name="Fit"))
            fig.update_layout(xaxis_title="X",yaxis_title="Y")
            st.plotly_chart(fig,use_container_width=True)
        except Exception: st.warning("Enter equal-length numeric arrays.")

# ---------------- Environmental ----------------
elif section == "🌱 Environmental Biotechnology":
    tool = st.selectbox("Environmental tool", [
        "Removal efficiency", "Loading rate", "EBRT", "H₂S removal", "Concentration conversion"
    ])
    if tool == "Removal efficiency":
        cin=st.number_input("Influent concentration", value=100.0)
        cout=st.number_input("Effluent concentration", value=20.0)
        rem=(cin-cout)/cin*100 if cin else 0
        st.metric("Removal efficiency", f"{rem:.4g}%")
        st.markdown('<div class="formula">Removal (%) = (Cᵢₙ − Cₒᵤₜ) / Cᵢₙ × 100</div>', unsafe_allow_html=True)

    elif tool == "Loading rate":
        concentration=st.number_input("Concentration", value=100.0, min_value=0.0)
        flow=st.number_input("Flow rate", value=1.0, min_value=0.000001)
        reactor=st.number_input("Reactor/bed volume", value=1.0, min_value=0.000001)
        rate=concentration*flow/reactor
        st.metric("Volumetric loading", f"{rate:.6g} concentration·flow/volume")
        st.caption("Confirm unit consistency before interpreting the result.")

    elif tool == "EBRT":
        volume=st.number_input("Bioreactor/bed volume", value=1.0, min_value=0.000001)
        flow=st.number_input("Gas/liquid flow rate", value=1.0, min_value=0.000001)
        ebrt=volume/flow
        st.metric("EBRT", f"{ebrt:.6g} time units")
        st.markdown('<div class="formula">EBRT = reactor volume ÷ volumetric flow rate</div>', unsafe_allow_html=True)

    elif tool == "H₂S removal":
        cin=st.number_input("H₂S inlet concentration", value=500.0)
        cout=st.number_input("H₂S outlet concentration", value=50.0)
        flow=st.number_input("Gas flow rate", value=1.0, min_value=0.000001)
        removal=(cin-cout)/cin*100 if cin else 0
        load=(cin-cout)*flow
        c1,c2=st.columns(2)
        c1.metric("Removal", f"{removal:.4g}%")
        c2.metric("Removed concentration × flow", f"{load:.6g}")

    elif tool == "Concentration conversion":
        st.subheader("Simple concentration conversion")
        value=st.number_input("Value", value=1.0)
        from_unit=st.selectbox("From", ["mg/L","µg/L","g/L","ppm (water, approx.)"])
        to_unit=st.selectbox("To", ["mg/L","µg/L","g/L","ppm (water, approx.)"])
        factors={"µg/L":0.001,"mg/L":1.0,"g/L":1000.0,"ppm (water, approx.)":1.0}
        converted=value*factors[from_unit]/factors[to_unit]
        st.metric("Converted value", f"{converted:.6g} {to_unit}")
        st.caption("The ppm≈mg/L shortcut is approximate for dilute aqueous systems.")

# ---------------- Data Analyzer ----------------
elif section == "📈 Data Analyzer":
    st.subheader("Upload and explore your research data")
    uploaded = st.file_uploader("Upload Excel or CSV", type=["xlsx","csv"])
    if not uploaded:
        st.info("Upload a dataset to begin. Recommended structure: one observation per row, with columns such as Group, Replicate, Time, Concentration.")
    else:
        df = pd.read_csv(uploaded) if uploaded.name.endswith(".csv") else pd.read_excel(uploaded)
        st.success(f"Loaded {len(df):,} rows × {len(df.columns):,} columns")
        st.dataframe(df.head(100), use_container_width=True)

        numeric = df.select_dtypes(include=np.number).columns.tolist()
        tabs = st.tabs(["Summary","Plot","Correlation","Replicates"])
        with tabs[0]:
            st.dataframe(df[numeric].describe().T if numeric else df.describe(include="all").T, use_container_width=True)
        with tabs[1]:
            if numeric:
                y = st.selectbox("Y-axis", numeric)
                x_options = [c for c in df.columns if c != y]
                x = st.selectbox("X-axis", x_options) if x_options else None
                color = st.selectbox("Group/color (optional)", ["None"] + [c for c in df.columns if c not in [x,y]])
                if x:
                    fig=px.scatter(df,x=x,y=y,color=None if color=="None" else color,trendline="ols")
                    st.plotly_chart(fig,use_container_width=True)
                    st.download_button("⬇️ Download interactive plot HTML", fig.to_html(include_plotlyjs="cdn").encode(), "scimantra_plot.html")
        with tabs[2]:
            if len(numeric)>=2:
                corr=df[numeric].corr(numeric_only=True)
                fig=px.imshow(corr,text_auto=".2f",aspect="auto",title="Correlation heatmap")
                st.plotly_chart(fig,use_container_width=True)
            else:
                st.info("Need at least two numeric columns.")
        with tabs[3]:
            rep_col = st.selectbox("Replicate column", ["None"] + list(df.columns))
            value_col = st.selectbox("Measurement column", numeric if numeric else ["None"])
            if rep_col!="None" and value_col!="None":
                summary=df.groupby(rep_col)[value_col].agg(["count","mean","std","sem","min","max"]).reset_index()
                st.dataframe(summary,use_container_width=True)
                download_df(summary,"replicate_summary.csv")

# ---------------- Research ----------------
elif section == "🔬 Research Tools":
    tool = st.selectbox("Research utility", [
        "Standard curve", "Experimental design planner", "Manuscript checklist"
    ])
    if tool == "Standard curve":
        st.subheader("Standard Curve Generator")
        x_text=st.text_area("Known concentrations", "0,10,20,40,80,100")
        y_text=st.text_area("Measured response", "0.02,0.11,0.21,0.42,0.83,1.02")
        unknown=st.number_input("Unknown response to estimate", value=0.55)
        try:
            x=np.array([float(v) for v in x_text.split(",") if v.strip()])
            y=np.array([float(v) for v in y_text.split(",") if v.strip()])
            fit=stats.linregress(x,y)
            r2=fit.rvalue**2
            estimated=(unknown-fit.intercept)/fit.slope
            c1,c2,c3=st.columns(3)
            c1.metric("Slope",f"{fit.slope:.6g}")
            c2.metric("Intercept",f"{fit.intercept:.6g}")
            c3.metric("R²",f"{r2:.6g}")
            st.metric("Estimated unknown concentration",f"{estimated:.6g}")
            xx=np.linspace(x.min(),x.max(),100)
            fig=go.Figure()
            fig.add_trace(go.Scatter(x=x,y=y,mode="markers",name="Standards"))
            fig.add_trace(go.Scatter(x=xx,y=fit.intercept+fit.slope*xx,mode="lines",name="Regression"))
            fig.add_hline(y=unknown,line_dash="dash")
            fig.update_layout(xaxis_title="Concentration",yaxis_title="Response")
            st.plotly_chart(fig,use_container_width=True)
        except Exception:
            st.warning("Enter equal-length numeric arrays.")

    elif tool == "Experimental design planner":
        st.subheader("Simple Experimental Design Planner")
        groups=st.number_input("Number of experimental groups",min_value=1,max_value=50,value=3)
        replicates=st.number_input("Biological/independent replicates per group",min_value=1,max_value=100,value=3)
        technical=st.number_input("Technical measurements per replicate",min_value=1,max_value=20,value=1)
        total=int(groups*replicates*technical)
        st.metric("Total measurements",total)
        rows=[]
        for g in range(1,int(groups)+1):
            for r in range(1,int(replicates)+1):
                for t in range(1,int(technical)+1):
                    rows.append([f"Group {g}",f"R{r}",f"T{t}"])
        plan=pd.DataFrame(rows,columns=["Group","Replicate","Technical"])
        st.dataframe(plan,use_container_width=True)
        download_df(plan,"experimental_design_plan.csv")
        st.caption("Use independent biological replicates for inferential statistics; technical replicates are repeated measurements, not independent biological samples.")

    elif tool == "Manuscript checklist":
        st.subheader("Research Manuscript Checklist")
        items=[
            "Research question/objective is clearly stated",
            "Appropriate controls are described",
            "Replicates are clearly defined",
            "Methods contain enough detail for reproducibility",
            "Statistical tests match the experimental design",
            "Raw/processed data are organized",
            "Figures have clear labels and units",
            "Error bars are defined",
            "p-values/effect sizes are reported appropriately",
            "Results are separated from interpretation",
            "Discussion connects findings to literature",
            "Limitations are acknowledged",
            "References are checked",
            "Abstract matches the final results",
        ]
        done=0
        for item in items:
            if st.checkbox(item): done+=1
        st.progress(done/len(items))
        st.write(f"Completed: **{done}/{len(items)}**")

st.divider()
st.caption("SciMantra Research Tools • Educational/research aid. Verify calculations against the standard method, SOP, instrument protocol, and applicable scientific guidelines before use.")
