import math
import numpy as np
import pandas as pd
import streamlit as st
from scipy import stats
from scipy.optimize import brentq
import plotly.express as px
import plotly.graph_objects as go

from src.scimantra.laboratory import (
    molarity_from_mass,
    dilution_stock_volume,
    solution_percentage,
    normality_from_molarity,
    cfu_per_ml,
    biomass_concentration,
    growth_rate,
    specific_growth_rate,
    bod_approx,
    cod_from_titration,
)
from src.scimantra.environmental import (
    removal_efficiency,
    loading_rate,
    ebrt,
    h2s_removal,
)

st.set_page_config(page_title="SciMantra Research Tools", page_icon="🔬", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
.block-container { max-width: 1400px; padding-top: 1.5rem; }
.hero { padding: 1.5rem 1.7rem; border-radius: 18px; background: linear-gradient(135deg,#e8f3ff,#f8fbff); border: 1px solid #d7e8fa; margin-bottom: 1rem; }
.hero h1 { margin:0; color:#0b1f33; font-size:2.35rem; }
.hero p { margin:.4rem 0 0; color:#38536b; font-size:1.05rem; }
.tool-card { border:1px solid #e3eaf0; border-radius:14px; padding:1rem; background:white; min-height:120px; }
.formula { background:#f7f9fb; padding:.7rem 1rem; border-radius:10px; border-left:4px solid #1565c0; }
footer { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero"><h1>🔬 SciMantra Research Tools</h1><p>Calculate • Analyze • Visualize • Understand — practical tools for science, laboratory work and research.</p></div>
""", unsafe_allow_html=True)

st.sidebar.title("SCIMantra")
st.sidebar.caption("Science • Research • Learning")
section = st.sidebar.radio("Choose a tool", [
    "🏠 Dashboard", "🧪 Laboratory Calculators", "📊 Statistics", "🌱 Environmental Biotechnology",
    "📈 Data Analyzer", "📊 Advanced Analysis", "🔬 Research Tools", "🌍 TEA & LCA"
])

def download_df(df, filename="scimantra_results.csv"):
    st.download_button("⬇️ Download CSV", df.to_csv(index=False).encode("utf-8"), filename, "text/csv")

def irr_roots(cashflows, max_rate=1000.0):
    cf=np.asarray(cashflows,dtype=float)
    if len(cf)<2 or not (np.any(cf>0) and np.any(cf<0)): return []
    def f(r): return sum(v/((1+r)**i) for i,v in enumerate(cf))
    grid=np.unique(np.concatenate(([-.9999,-.99,-.9,-.5,-.1,0.0],np.geomspace(1e-8,max_rate,300))))
    vals=[f(float(r)) for r in grid]; roots=[]
    for i in range(len(grid)-1):
        a,b=float(grid[i]),float(grid[i+1]); fa,fb=vals[i],vals[i+1]
        if not(np.isfinite(fa) and np.isfinite(fb)): continue
        if fa==0: roots.append(a)
        elif fa*fb<0:
            try:
                root=brentq(f,a,b)
                if not roots or abs(root-roots[-1])>1e-6: roots.append(root)
            except Exception: pass
    return roots

def npv_of(cf, rate): return sum(v/((1+rate)**i) for i,v in enumerate(cf))
def payback(cf, discounted=False, rate=0.0):
    cumulative=0.0
    for i,v in enumerate(cf):
        pv=v/((1+rate)**i) if discounted else v
        prev=cumulative; cumulative+=pv
        if cumulative>=0 and i>0:
            return float(i) if pv==0 else (i-1)+max(0,min(1,-prev/pv))
    return np.nan

if section == "📊 Advanced Analysis":
    import runpy
    runpy.run_path("pages/7_Advanced_Experimental_Data_Analysis.py")
    st.stop()

if section == "🏠 Dashboard":
    st.subheader("Research tools in one place")
    cols=st.columns(3)
    cards=[("🧪 Laboratory","Molarity, dilution, CFU/mL, BOD, COD, biomass and growth calculations."),("📊 Statistics","Mean, SD, SEM, CV, t-test, ANOVA, correlation and regression."),("🌱 Environment","Removal efficiency, loading, EBRT and H₂S analysis."),("📈 Data Analyzer","Upload Excel/CSV files, summarize replicates and create interactive graphs."),("📊 Advanced Analysis","Replicate-aware statistics, regression, time-series and research-grade visualization."),("🔬 Research","Standard curves, experimental design and manuscript checklists."),("🌍 TEA & LCA","Screen process economics, NPV, IRR, life-cycle inventory and CO₂e intensity.")]
    for i,(title,desc) in enumerate(cards):
        with cols[i%3]: st.markdown(f'<div class="tool-card"><h3>{title}</h3><p>{desc}</p></div>',unsafe_allow_html=True)
    st.info("Tip: use Advanced Experimental Data Analysis for replicate-aware datasets, or TEA & LCA for process sustainability evaluation.")

elif section == "🧪 Laboratory Calculators":
    tool=st.selectbox("Calculator",["Molarity","Dilution (C₁V₁ = C₂V₂)","% Solution","Normality","CFU/mL","Biomass concentration","Growth rate","Specific growth rate","BOD","COD"])
    if tool=="Molarity":
        mass=st.number_input("Mass of solute (g)",min_value=0.,value=1.); mw=st.number_input("Molecular weight (g/mol)",min_value=1e-6,value=58.44); vol=st.number_input("Final volume (L)",min_value=1e-6,value=1.); st.metric("Molarity",f"{molarity_from_mass(mass,mw,vol):.6g} mol/L")
    elif tool.startswith("Dilution"):
        c1=st.number_input("C₁",min_value=0.,value=100.); c2=st.number_input("C₂",min_value=1e-6,value=10.); v2=st.number_input("V₂",min_value=1e-6,value=100.)
        try:
            v1=dilution_stock_volume(c1,c2,v2)
            st.metric("Stock volume V₁",f"{v1:.4g}"); st.metric("Diluent volume",f"{v2-v1:.4g}")
        except ValueError as exc: st.error(str(exc))
    elif tool=="% Solution":
        st.selectbox("Type",["w/v","w/w","v/v"]); amount=st.number_input("Solute amount",min_value=0.,value=5.); total=st.number_input("Total amount/volume",min_value=1e-6,value=100.); st.metric("Percentage",f"{solution_percentage(amount,total):.4g}%")
    elif tool=="Normality":
        m=st.number_input("Molarity (mol/L)",min_value=0.,value=1.); n=st.number_input("n-factor",min_value=1e-6,value=1.); st.metric("Normality",f"{normality_from_molarity(m,n):.6g} N")
    elif tool=="CFU/mL":
        colonies=st.number_input("Colonies",min_value=0.,value=125.); dilution=st.number_input("Reciprocal dilution",min_value=1.,value=100000.); plated=st.number_input("Volume plated (mL)",min_value=1e-6,value=.1); st.metric("CFU/mL",f"{cfu_per_ml(colonies,dilution,plated):.6g}")
    elif tool=="Biomass concentration":
        dry=st.number_input("Dry biomass (g)",min_value=0.,value=1.); v=st.number_input("Culture volume (L)",min_value=1e-6,value=1.); st.metric("Biomass",f"{biomass_concentration(dry,v):.6g} g/L")
    elif tool=="Growth rate":
        x1=st.number_input("Measurement 1",value=.1); x2=st.number_input("Measurement 2",value=.8); t1=st.number_input("Time 1",value=0.); t2=st.number_input("Time 2",value=10.)
        try: st.metric("Growth rate",f"{growth_rate(x1,x2,t1,t2):.6g}")
        except ValueError: st.metric("Growth rate","N/A")
    elif tool=="Specific growth rate":
        x1=st.number_input("X₁",min_value=1e-6,value=.1); x2=st.number_input("X₂",min_value=1e-6,value=.8); dt=st.number_input("Δt",min_value=1e-6,value=10.); st.metric("μ",f"{specific_growth_rate(x1,x2,dt):.6g} time⁻¹")
    elif tool=="BOD":
        initial=st.number_input("Initial DO (mg/L)",value=8.); final=st.number_input("Final DO (mg/L)",value=3.); sample=st.number_input("Sample volume (mL)",min_value=1e-6,value=15.); bottle=st.number_input("Bottle volume (mL)",min_value=1e-6,value=300.); st.metric("Approx. BOD₅",f"{bod_approx(initial,final,sample,bottle):.6g} mg/L")
    else:
        a=st.number_input("Blank titration A (mL)",value=20.); b=st.number_input("Sample titration B (mL)",value=12.); normality=st.number_input("Titrant normality",min_value=1e-6,value=.1); volume=st.number_input("Sample volume (mL)",min_value=1e-6,value=10.); st.metric("COD",f"{cod_from_titration(a,b,normality,volume):.6g} mg/L")

elif section == "📊 Statistics":
    tool=st.selectbox("Statistical tool",["Descriptive statistics","t-Test","One-way ANOVA","Correlation","Linear regression"])
    if tool=="Descriptive statistics":
        vals=st.text_area("Values separated by commas","1,2,3,4,5,6")
        try:
            x=np.array([float(v.strip()) for v in vals.split(",") if v.strip()]); c=st.columns(4); c[0].metric("Mean",f"{x.mean():.5g}"); c[1].metric("SD",f"{x.std(ddof=1):.5g}" if len(x)>1 else "NA"); c[2].metric("SEM",f"{stats.sem(x):.5g}" if len(x)>1 else "NA"); c[3].metric("CV %",f"{x.std(ddof=1)/x.mean()*100:.5g}" if len(x)>1 and x.mean()!=0 else "NA")
        except Exception: st.error("Please enter numeric values.")
    elif tool=="t-Test":
        a=st.text_area("Group A","1,2,3,4,5"); b=st.text_area("Group B","2,3,4,5,6")
        try:
            x=[float(v) for v in a.split(",") if v.strip()]; y=[float(v) for v in b.split(",") if v.strip()]; r=stats.ttest_ind(x,y,equal_var=False); st.metric("t statistic",f"{r.statistic:.6g}"); st.metric("p-value",f"{r.pvalue:.6g}")
        except Exception: st.warning("Enter two numeric groups.")
    elif tool=="One-way ANOVA":
        txt=st.text_area("Groups, one per line","1,2,3\n2,3,4\n5,6,7")
        try: groups=[[float(v) for v in line.split(",") if v.strip()] for line in txt.splitlines() if line.strip()]; r=stats.f_oneway(*groups); st.metric("F statistic",f"{r.statistic:.6g}"); st.metric("p-value",f"{r.pvalue:.6g}")
        except Exception: st.warning("Enter numeric groups.")
    elif tool=="Correlation":
        x=st.text_area("X values","1,2,3,4,5"); y=st.text_area("Y values","2,4,5,8,10"); method=st.selectbox("Method",["Pearson","Spearman"])
        try: xx=np.array([float(v) for v in x.split(",") if v.strip()]); yy=np.array([float(v) for v in y.split(",") if v.strip()]); r=stats.pearsonr(xx,yy) if method=="Pearson" else stats.spearmanr(xx,yy); st.metric("Coefficient",f"{r.statistic:.6g}"); st.metric("p-value",f"{r.pvalue:.6g}")
        except Exception: st.warning("Enter equal-length arrays.")
    else:
        x=st.text_area("X values","1,2,3,4,5"); y=st.text_area("Y values","2,4,5,8,10")
        try: xx=np.array([float(v) for v in x.split(",") if v.strip()]); yy=np.array([float(v) for v in y.split(",") if v.strip()]); r=stats.linregress(xx,yy); c=st.columns(4); c[0].metric("Slope",f"{r.slope:.6g}"); c[1].metric("Intercept",f"{r.intercept:.6g}"); c[2].metric("R²",f"{r.rvalue**2:.6g}"); c[3].metric("p-value",f"{r.pvalue:.6g}"); order=np.argsort(xx); st.plotly_chart(go.Figure([go.Scatter(x=xx,y=yy,mode="markers"),go.Scatter(x=xx[order],y=r.intercept+r.slope*xx[order],mode="lines")]),width="stretch")
        except Exception: st.warning("Enter equal-length arrays.")

elif section == "🌱 Environmental Biotechnology":
    tool=st.selectbox("Environmental tool",["Removal efficiency","Loading rate","EBRT","H₂S removal"])
    if tool=="Removal efficiency":
        cin=st.number_input("Influent concentration",value=100.); cout=st.number_input("Effluent concentration",value=20.)
        try: st.metric("Removal efficiency",f"{removal_efficiency(cin,cout):.4g}%")
        except ValueError as exc: st.error(str(exc))
    elif tool=="Loading rate":
        concentration=st.number_input("Concentration",value=100.,min_value=0.); flow=st.number_input("Flow rate",value=1.,min_value=0.)
        try: st.metric("Loading",f"{loading_rate(concentration,flow):.6g} mass/time")
        except ValueError as exc: st.error(str(exc))
    elif tool=="EBRT":
        volume=st.number_input("Reactor volume",value=1.,min_value=0.); flow=st.number_input("Gas flow",value=1.,min_value=0.)
        try: st.metric("EBRT",f"{ebrt(volume,flow):.6g} time")
        except ValueError as exc: st.error(str(exc))
    else:
        cin=st.number_input("H₂S inlet",value=100.); cout=st.number_input("H₂S outlet",value=20.)
        try: st.metric("H₂S removal",f"{h2s_removal(cin,cout):.4g}%")
        except ValueError as exc: st.error(str(exc))

elif section == "📈 Data Analyzer":
    st.subheader("Data Analyzer")
    uploaded=st.file_uploader("Upload Excel/CSV",type=["xlsx","csv"])
    if uploaded:
        df=pd.read_csv(uploaded) if uploaded.name.lower().endswith(".csv") else pd.read_excel(uploaded)
        st.dataframe(df,width="stretch")
        numeric=df.select_dtypes(include=np.number).columns.tolist()
        if numeric:
            col=st.selectbox("Variable",numeric); st.dataframe(df[col].describe().to_frame().T,width="stretch"); st.plotly_chart(px.histogram(df,x=col,title=f"Distribution: {col}"),width="stretch")
    else: st.info("Upload an Excel or CSV file to begin.")

elif section == "🔬 Research Tools":
    st.subheader("Research Utilities")
    tool=st.selectbox("Tool",["Standard curve","Experimental design checklist","Manuscript checklist"])
    if tool=="Standard curve":
        x=st.text_input("Concentrations", "1,2,3,4,5"); y=st.text_input("Response", "2,4,5,8,10")
        try:
            xx=np.array([float(v) for v in x.split(",") if v.strip()]); yy=np.array([float(v) for v in y.split(",") if v.strip()]); r=stats.linregress(xx,yy); st.metric("R²",f"{r.rvalue**2:.6g}"); order=np.argsort(xx); st.plotly_chart(go.Figure([go.Scatter(x=xx,y=yy,mode="markers"),go.Scatter(x=xx[order],y=r.intercept+r.slope*xx[order],mode="lines")]),width="stretch")
        except Exception: st.warning("Enter equal-length numeric arrays.")
    elif tool=="Experimental design checklist":
        for item in ["Define hypothesis","Identify independent/dependent variables","Choose controls","Set biological/technical replicates","Define sample size","Predefine statistical analysis","Document units and conditions"]: st.checkbox(item)
    else:
        for item in ["Title and abstract","Methods reproducibility","Statistical reporting","Figures and tables","References","Limitations","Data/code availability"]: st.checkbox(item)

elif section == "🌍 TEA & LCA":
    st.subheader("Techno-Economic Analysis & Life-Cycle Assessment")
    st.caption("Screening-level calculations for research planning; document assumptions and verify with project-specific data.")
    st.write("Use the existing TEA & LCA tools below to model NPV, IRR, payback, inventory and CO₂e intensity.")
