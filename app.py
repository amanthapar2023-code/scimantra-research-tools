import math
import numpy as np
import pandas as pd
import streamlit as st
from scipy import stats
from scipy.optimize import brentq
import plotly.express as px
import plotly.graph_objects as go

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
<div class="hero">
<h1>🔬 SciMantra Research Tools</h1>
<p>Calculate • Analyze • Visualize • Understand — practical tools for science, laboratory work and research.</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.title("SCIMantra")
st.sidebar.caption("Science • Research • Learning")
section = st.sidebar.radio("Choose a tool", [
    "🏠 Dashboard", "🧪 Laboratory Calculators", "📊 Statistics",
    "🌱 Environmental Biotechnology", "📈 Data Analyzer", "🔬 Research Tools",
    "🌍 TEA & LCA"
])

def download_df(df, filename="scimantra_results.csv"):
    st.download_button("⬇️ Download CSV", df.to_csv(index=False).encode("utf-8"), filename, "text/csv")

def irr_from_cashflows(cashflows):
    cf = np.asarray(cashflows, dtype=float)
    if len(cf) < 2 or not (np.any(cf > 0) and np.any(cf < 0)):
        return np.nan
    def npv_fn(rate):
        return sum(v / ((1 + rate) ** i) for i, v in enumerate(cf))
    try:
        return brentq(npv_fn, -0.9999, 100.0)
    except Exception:
        return np.nan

def payback(cashflows, discounted=False, rate=0.0):
    cumulative = 0.0
    for i, v in enumerate(cashflows):
        pv = v / ((1 + rate) ** i) if discounted else v
        previous = cumulative
        cumulative += pv
        if cumulative >= 0 and i > 0:
            return (i - 1) + max(0.0, min(1.0, -previous / pv)) if pv else float(i)
    return np.nan

if section == "🏠 Dashboard":
    st.subheader("Research tools in one place")
    cols = st.columns(3)
    cards = [
        ("🧪 Laboratory", "Molarity, dilution, CFU/mL, BOD, COD, biomass and growth calculations."),
        ("📊 Statistics", "Mean, SD, SEM, CV, t-test, ANOVA, correlation and regression."),
        ("🌱 Environment", "Removal efficiency, loading, EBRT and H₂S analysis."),
        ("📈 Data Analyzer", "Upload Excel/CSV files, summarize replicates and create interactive graphs."),
        ("🔬 Research", "Standard curves, experimental design and manuscript checklists."),
        ("🌍 TEA & LCA", "Screen process economics, NPV, IRR, life-cycle inventory and CO₂e intensity."),
    ]
    for i, (title, desc) in enumerate(cards):
        with cols[i % 3]:
            st.markdown(f'<div class="tool-card"><h3>{title}</h3><p>{desc}</p></div>', unsafe_allow_html=True)
    st.info("Tip: start with Data Analyzer for an Excel/CSV dataset, or TEA & LCA for process sustainability evaluation.")

elif section == "🧪 Laboratory Calculators":
    tool = st.selectbox("Calculator", ["Molarity","Dilution (C₁V₁ = C₂V₂)","% Solution","Normality","CFU/mL","Biomass concentration","Growth rate","Specific growth rate","BOD","COD"])
    if tool == "Molarity":
        st.subheader("Molarity Calculator")
        mass=st.number_input("Mass of solute (g)",min_value=0.0,value=1.0); mw=st.number_input("Molecular weight (g/mol)",min_value=0.000001,value=58.44); vol=st.number_input("Final volume (L)",min_value=0.000001,value=1.0)
        st.metric("Molarity",f"{mass/mw/vol:.6g} mol/L")
    elif tool == "Dilution (C₁V₁ = C₂V₂)":
        st.subheader("Dilution Calculator")
        c1=st.number_input("C₁ (stock concentration)",min_value=0.0,value=100.0); c2=st.number_input("C₂ (desired concentration)",min_value=0.000001,value=10.0); v2=st.number_input("V₂ (final volume)",min_value=0.000001,value=100.0)
        v1=c2*v2/c1 if c1 else 0; st.metric("Stock volume V₁",f"{v1:.4g}"); st.metric("Diluent volume",f"{v2-v1:.4g}")
    elif tool == "% Solution":
        st.subheader("Percentage Solution"); st.selectbox("Type",["w/v (% g per 100 mL)","w/w (% g per 100 g)","v/v (% mL per 100 mL)"])
        amount=st.number_input("Solute amount",min_value=0.0,value=5.0); total=st.number_input("Total amount/volume",min_value=0.000001,value=100.0); st.metric("Percentage",f"{amount/total*100:.4g}%")
    elif tool == "Normality":
        st.subheader("Normality Calculator"); m=st.number_input("Molarity (mol/L)",min_value=0.0,value=1.0); n=st.number_input("n-factor / equivalent factor",min_value=0.000001,value=1.0); st.metric("Normality",f"{m*n:.6g} N")
    elif tool == "CFU/mL":
        st.subheader("CFU/mL Calculator"); colonies=st.number_input("Colonies counted",min_value=0.0,value=125.0); dilution=st.number_input("Reciprocal dilution",min_value=1.0,value=100000.0); plated=st.number_input("Volume plated (mL)",min_value=0.000001,value=0.1); st.metric("CFU/mL",f"{colonies*dilution/plated:.6g}")
    elif tool == "Biomass concentration":
        st.subheader("Biomass Concentration"); dry=st.number_input("Dry biomass (g)",min_value=0.0,value=1.0); v=st.number_input("Culture volume (L)",min_value=0.000001,value=1.0); st.metric("Biomass",f"{dry/v:.6g} g/L")
    elif tool == "Growth rate":
        st.subheader("Average Growth Rate"); x1=st.number_input("Measurement 1",value=0.1); x2=st.number_input("Measurement 2",value=0.8); t1=st.number_input("Time 1",value=0.0); t2=st.number_input("Time 2",value=10.0); st.metric("Growth rate",f"{(x2-x1)/(t2-t1):.6g} units/time" if t2!=t1 else "0")
    elif tool == "Specific growth rate":
        st.subheader("Specific Growth Rate"); x1=st.number_input("X₁",min_value=0.000001,value=0.1); x2=st.number_input("X₂",min_value=0.000001,value=0.8); dt=st.number_input("Δt",min_value=0.000001,value=10.0); st.metric("μ",f"{math.log(x2/x1)/dt:.6g} time⁻¹")
    elif tool == "BOD":
        st.subheader("BOD Calculator"); initial=st.number_input("Initial DO (mg/L)",value=8.0); final=st.number_input("Final DO (mg/L)",value=3.0); sample=st.number_input("Sample volume (mL)",value=15.0,min_value=0.000001); bottle=st.number_input("Bottle volume (mL)",value=300.0,min_value=0.000001); st.metric("Approx. BOD₅",f"{(initial-final)*bottle/sample:.6g} mg/L"); st.caption("Apply the appropriate standard-method seed, dilution-water and blank corrections where applicable.")
    elif tool == "COD":
        st.subheader("COD Calculator"); a=st.number_input("Blank titration A (mL)",value=20.0); b=st.number_input("Sample titration B (mL)",value=12.0); normality=st.number_input("Titrant normality",value=0.1,min_value=0.000001); volume=st.number_input("Sample volume (mL)",value=10.0,min_value=0.000001); st.metric("COD",f"{(a-b)*normality*8000/volume:.6g} mg/L"); st.caption("Verify the reagent-specific equation and laboratory method.")

elif section == "📊 Statistics":
    tool=st.selectbox("Statistical tool",["Descriptive statistics","t-Test","One-way ANOVA","Correlation","Linear regression"])
    uploaded=st.file_uploader("Upload CSV/Excel (optional)",type=["csv","xlsx"]); df=None
    if uploaded:
        df=pd.read_csv(uploaded) if uploaded.name.endswith(".csv") else pd.read_excel(uploaded); st.dataframe(df.head(20),use_container_width=True)
    if tool == "Descriptive statistics":
        if df is not None:
            numeric=df.select_dtypes(include=np.number); result=numeric.describe().T; result["SEM"]=numeric.sem(); result["CV_%"]=numeric.std(ddof=1)/numeric.mean()*100; st.dataframe(result,use_container_width=True); download_df(result.reset_index().rename(columns={"index":"Variable"}),"descriptive_statistics.csv")
        else:
            vals=st.text_area("Enter values separated by commas","1,2,3,4,5,6")
            try:
                x=np.array([float(v.strip()) for v in vals.split(",") if v.strip()]); c=st.columns(4); c[0].metric("Mean",f"{x.mean():.5g}"); c[1].metric("SD",f"{x.std(ddof=1):.5g}" if len(x)>1 else "NA"); c[2].metric("SEM",f"{stats.sem(x):.5g}" if len(x)>1 else "NA"); c[3].metric("CV %",f"{x.std(ddof=1)/x.mean()*100:.5g}" if len(x)>1 and x.mean()!=0 else "NA")
            except Exception: st.error("Please enter numeric values.")
    elif tool == "t-Test":
        a=st.text_area("Group A","1,2,3,4,5"); b=st.text_area("Group B","2,3,4,5,6")
        try:
            x=[float(v) for v in a.split(",") if v.strip()]; y=[float(v) for v in b.split(",") if v.strip()]; r=stats.ttest_ind(x,y,equal_var=False); st.metric("t statistic",f"{r.statistic:.6g}"); st.metric("p-value",f"{r.pvalue:.6g}"); st.caption("Welch's independent two-sample t-test.")
        except Exception: st.warning("Enter two comma-separated numeric groups.")
    elif tool == "One-way ANOVA":
        txt=st.text_area("Groups (one group per line)","1,2,3\n2,3,4\n5,6,7")
        try:
            groups=[[float(v) for v in line.split(",") if v.strip()] for line in txt.splitlines() if line.strip()]; r=stats.f_oneway(*groups); st.metric("F statistic",f"{r.statistic:.6g}"); st.metric("p-value",f"{r.pvalue:.6g}"); st.caption("ANOVA tests whether at least one group mean differs; post-hoc tests may be needed.")
        except Exception: st.warning("Enter numeric groups, one group per line.")
    elif tool == "Correlation":
        x=st.text_area("X values","1,2,3,4,5"); y=st.text_area("Y values","2,4,5,8,10"); method=st.selectbox("Method",["Pearson","Spearman"])
        try:
            xx=np.array([float(v) for v in x.split(",") if v.strip()]); yy=np.array([float(v) for v in y.split(",") if v.strip()]); r=stats.pearsonr(xx,yy) if method=="Pearson" else stats.spearmanr(xx,yy); st.metric("Correlation coefficient",f"{r.statistic:.6g}"); st.metric("p-value",f"{r.pvalue:.6g}")
        except Exception: st.warning("Enter equal-length numeric arrays.")
    elif tool == "Linear regression":
        x=st.text_area("X values","1,2,3,4,5"); y=st.text_area("Y values","2,4,5,8,10")
        try:
            xx=np.array([float(v) for v in x.split(",") if v.strip()]); yy=np.array([float(v) for v in y.split(",") if v.strip()]); r=stats.linregress(xx,yy); c=st.columns(4); c[0].metric("Slope",f"{r.slope:.6g}"); c[1].metric("Intercept",f"{r.intercept:.6g}"); c[2].metric("R²",f"{r.rvalue**2:.6g}"); c[3].metric("p-value",f"{r.pvalue:.6g}"); order=np.argsort(xx); fig=go.Figure([go.Scatter(x=xx,y=yy,mode="markers",name="Data"),go.Scatter(x=xx[order],y=r.intercept+r.slope*xx[order],mode="lines",name="Fit")]); st.plotly_chart(fig,use_container_width=True)
        except Exception: st.warning("Enter equal-length numeric arrays.")

elif section == "🌱 Environmental Biotechnology":
    tool=st.selectbox("Environmental tool",["Removal efficiency","Loading rate","EBRT","H₂S removal","Concentration conversion"])
    if tool == "Removal efficiency":
        cin=st.number_input("Influent concentration",value=100.0); cout=st.number_input("Effluent concentration",value=20.0); st.metric("Removal efficiency",f"{(cin-cout)/cin*100:.4g}%" if cin else "0")
    elif tool == "Loading rate":
        concentration=st.number_input("Concentration",value=100.0,min_value=0.0); flow=st.number_input("Flow rate",value=1.0,min_value=0.000001); reactor=st.number_input("Reactor/bed volume",value=1.0,min_value=0.000001); st.metric("Volumetric loading",f"{concentration*flow/reactor:.6g}"); st.caption("Confirm unit consistency.")
    elif tool == "EBRT":
        volume=st.number_input("Bioreactor/bed volume",value=1.0,min_value=0.000001); flow=st.number_input("Gas/liquid flow rate",value=1.0,min_value=0.000001); st.metric("EBRT",f"{volume/flow:.6g} time units")
    elif tool == "H₂S removal":
        cin=st.number_input("H₂S inlet concentration",value=500.0); cout=st.number_input("H₂S outlet concentration",value=50.0); flow=st.number_input("Gas flow rate",value=1.0,min_value=0.000001); c1,c2=st.columns(2); c1.metric("Removal",f"{(cin-cout)/cin*100:.4g}%" if cin else "0"); c2.metric("Removed concentration × flow",f"{(cin-cout)*flow:.6g}")
    elif tool == "Concentration conversion":
        value=st.number_input("Value",value=1.0); fu=st.selectbox("From",["mg/L","µg/L","g/L","ppm (water, approx.)"]); tu=st.selectbox("To",["mg/L","µg/L","g/L","ppm (water, approx.)"]); factors={"µg/L":0.001,"mg/L":1.0,"g/L":1000.0,"ppm (water, approx.)":1.0}; st.metric("Converted value",f"{value*factors[fu]/factors[tu]:.6g} {tu}")

elif section == "📈 Data Analyzer":
    st.subheader("Upload and explore your research data")
    uploaded=st.file_uploader("Upload Excel or CSV",type=["xlsx","csv"])
    if not uploaded: st.info("Upload a dataset to begin. Recommended structure: one observation per row with columns such as Group, Replicate, Time and Concentration.")
    else:
        df=pd.read_csv(uploaded) if uploaded.name.endswith(".csv") else pd.read_excel(uploaded); st.success(f"Loaded {len(df):,} rows × {len(df.columns):,} columns"); st.dataframe(df.head(100),use_container_width=True); numeric=df.select_dtypes(include=np.number).columns.tolist(); tabs=st.tabs(["Summary","Plot","Correlation","Replicates"])
        with tabs[0]: st.dataframe(df[numeric].describe().T if numeric else df.describe(include="all").T,use_container_width=True)
        with tabs[1]:
            if numeric:
                y=st.selectbox("Y-axis",numeric); xopts=[c for c in df.columns if c!=y]; x=st.selectbox("X-axis",xopts) if xopts else None; color=st.selectbox("Group/color (optional)",["None"]+[c for c in df.columns if c not in [x,y]])
                if x:
                    fig=px.scatter(df,x=x,y=y,color=None if color=="None" else color,trendline="ols"); st.plotly_chart(fig,use_container_width=True); st.download_button("⬇️ Download interactive plot HTML",fig.to_html(include_plotlyjs="cdn").encode(),"scimantra_plot.html")
        with tabs[2]:
            if len(numeric)>=2: st.plotly_chart(px.imshow(df[numeric].corr(numeric_only=True),text_auto=".2f",aspect="auto",title="Correlation heatmap"),use_container_width=True)
            else: st.info("Need at least two numeric columns.")
        with tabs[3]:
            rep=st.selectbox("Replicate column",["None"]+list(df.columns)); val=st.selectbox("Measurement column",numeric if numeric else ["None"])
            if rep!="None" and val!="None": download_df(df.groupby(rep)[val].agg(["count","mean","std","sem","min","max"]).reset_index(),"replicate_summary.csv")

elif section == "🔬 Research Tools":
    tool=st.selectbox("Research utility",["Standard curve","Experimental design planner","Manuscript checklist"])
    if tool == "Standard curve":
        st.subheader("Standard Curve Generator"); xt=st.text_area("Known concentrations","0,10,20,40,80,100"); yt=st.text_area("Measured response","0.02,0.11,0.21,0.42,0.83,1.02"); unknown=st.number_input("Unknown response",value=0.55)
        try:
            x=np.array([float(v) for v in xt.split(",") if v.strip()]); y=np.array([float(v) for v in yt.split(",") if v.strip()]); fit=stats.linregress(x,y); st.metric("Estimated unknown concentration",f"{(unknown-fit.intercept)/fit.slope:.6g}"); c=st.columns(3); c[0].metric("Slope",f"{fit.slope:.6g}"); c[1].metric("Intercept",f"{fit.intercept:.6g}"); c[2].metric("R²",f"{fit.rvalue**2:.6g}"); xx=np.linspace(x.min(),x.max(),100); fig=go.Figure([go.Scatter(x=x,y=y,mode="markers",name="Standards"),go.Scatter(x=xx,y=fit.intercept+fit.slope*xx,mode="lines",name="Regression")]); st.plotly_chart(fig,use_container_width=True)
        except Exception: st.warning("Enter equal-length numeric arrays.")
    elif tool == "Experimental design planner":
        st.subheader("Experimental Design Planner"); groups=st.number_input("Experimental groups",1,50,3); reps=st.number_input("Independent replicates/group",1,100,3); tech=st.number_input("Technical measurements/replicate",1,20,1); total=int(groups*reps*tech); st.metric("Total measurements",total); rows=[[f"Group {g}",f"R{r}",f"T{t}"] for g in range(1,int(groups)+1) for r in range(1,int(reps)+1) for t in range(1,int(tech)+1)]; download_df(pd.DataFrame(rows,columns=["Group","Replicate","Technical"]),"experimental_design_plan.csv"); st.caption("Technical replicates are repeated measurements, not independent biological samples.")
    else:
        st.subheader("Research Manuscript Checklist"); items=["Research question/objective is clearly stated","Appropriate controls are described","Replicates are clearly defined","Methods contain enough detail for reproducibility","Statistical tests match the experimental design","Raw/processed data are organized","Figures have clear labels and units","Error bars are defined","p-values/effect sizes are reported appropriately","Results are separated from interpretation","Discussion connects findings to literature","Limitations are acknowledged","References are checked","Abstract matches the final results"]; done=sum(st.checkbox(i) for i in items); st.progress(done/len(items)); st.write(f"Completed: **{done}/{len(items)}**")

elif section == "🌍 TEA & LCA":
    st.header("🌍 Sustainability & Process Evaluation")
    st.caption("Techno-Economic Analysis (TEA) and Life Cycle Assessment (LCA) — transparent research decision-support tools")
    st.info("Screening-level models only. Define the system boundary, functional unit, currency, year, data sources and assumptions before using results in a publication, feasibility study or investment decision.")
    mode=st.radio("Choose analysis",["💰 Techno-Economic Analysis (TEA)","🌍 Life Cycle Assessment (LCA)"],horizontal=True)
    if mode.startswith("💰"):
        st.subheader("💰 Techno-Economic Analysis (TEA)")
        st.write("Estimate CAPEX, annual OPEX, revenue, cash flow, NPV, IRR, payback and break-even performance for a process, product or treatment system.")
        with st.expander("1. Project & production assumptions",expanded=True):
            c1,c2,c3=st.columns(3)
            with c1: currency=st.text_input("Currency symbol","₹"); years=st.number_input("Project life (years)",1,50,10); annual_output=st.number_input("Nameplate annual output / treatment capacity",min_value=0.000001,value=1000.0)
            with c2: unit=st.text_input("Output unit","kg or m³"); price=st.number_input("Selling value / avoided treatment cost per unit",min_value=0.0,value=100.0); capacity=st.number_input("Capacity factor (%)",0.0,100.0,90.0)
            with c3: discount=st.number_input("Discount rate (%)",0.0,100.0,10.0); tax=st.number_input("Tax rate (%)",0.0,100.0,25.0); salvage_pct=st.number_input("Salvage value (% of CAPEX)",0.0,100.0,5.0)
        with st.expander("2. Capital expenditure (CAPEX)",expanded=True):
            c1,c2,c3=st.columns(3)
            with c1: equipment=st.number_input("Equipment & process units",min_value=0.0,value=500000.0); installation=st.number_input("Installation & civil works",min_value=0.0,value=150000.0)
            with c2: engineering=st.number_input("Engineering / commissioning",min_value=0.0,value=75000.0); contingency_pct=st.number_input("Contingency (%)",0.0,100.0,10.0)
            with c3: other_capex=st.number_input("Other CAPEX",min_value=0.0,value=0.0); working_capital=st.number_input("Initial working capital",min_value=0.0,value=50000.0)
        direct_capex=equipment+installation+engineering+other_capex; contingency=direct_capex*contingency_pct/100; total_capex=direct_capex+contingency
        with st.expander("3. Annual operating expenditure (OPEX)",expanded=True):
            c1,c2,c3=st.columns(3)
            with c1: fixed=st.number_input("Fixed OPEX / year",min_value=0.0,value=100000.0); labor=st.number_input("Labor / year",min_value=0.0,value=120000.0)
            with c2: utilities=st.number_input("Utilities / year",min_value=0.0,value=80000.0); maint_pct=st.number_input("Maintenance (% of CAPEX/year)",0.0,100.0,4.0)
            with c3: var_cost=st.number_input(f"Variable cost / {unit}",min_value=0.0,value=20.0); other_opex=st.number_input("Other OPEX / year",min_value=0.0,value=0.0)
        effective=annual_output*capacity/100; maintenance=total_capex*maint_pct/100; revenue=effective*price; var_opex=effective*var_cost; annual_opex=fixed+labor+utilities+maintenance+var_opex+other_opex; ebitda=revenue-annual_opex; depreciation=total_capex/years; ebit=ebitda-depreciation; tax_exp=max(0.0,ebit*tax/100); fcf=ebit-tax_exp+depreciation; salvage=total_capex*salvage_pct/100
        cashflows=[-total_capex-working_capital]+[fcf]*int(years); cashflows[-1]+=salvage+working_capital; yr=np.arange(int(years)+1); dcf=[cashflows[i]/((1+discount/100)**i) for i in yr]; npv=sum(dcf); irr=irr_from_cashflows(cashflows); spb=payback(cashflows); dpb=payback(cashflows,True,discount/100); bep=(annual_opex+depreciation)/effective if effective else np.nan; margin=price-var_cost; bev=(fixed+labor+utilities+maintenance+other_opex)/margin if margin>0 else np.nan
        st.subheader("Key TEA results"); c=st.columns(6); c[0].metric("Total CAPEX",f"{currency}{total_capex:,.0f}"); c[1].metric("Annual revenue",f"{currency}{revenue:,.0f}"); c[2].metric("Annual OPEX",f"{currency}{annual_opex:,.0f}"); c[3].metric("Annual FCF",f"{currency}{fcf:,.0f}"); c[4].metric("NPV",f"{currency}{npv:,.0f}"); c[5].metric("IRR",f"{irr*100:.2f}%" if np.isfinite(irr) else "N/A")
        c=st.columns(4); c[0].metric("Simple payback",f"{spb:.2f} years" if np.isfinite(spb) else "Not reached"); c[1].metric("Discounted payback",f"{dpb:.2f} years" if np.isfinite(dpb) else "Not reached"); c[2].metric("Break-even value / unit",f"{currency}{bep:,.2f}" if np.isfinite(bep) else "N/A"); c[3].metric("Break-even annual volume",f"{bev:,.2f}" if np.isfinite(bev) else "N/A")
        cf=pd.DataFrame({"Year":yr,"Cash flow":cashflows,"Discounted cash flow":dcf,"Cumulative cash flow":np.cumsum(cashflows),"Cumulative discounted cash flow":np.cumsum(dcf)}); st.plotly_chart(px.line(cf,x="Year",y=["Cumulative cash flow","Cumulative discounted cash flow"],markers=True,title="Cumulative project cash flow"),use_container_width=True); st.dataframe(cf,use_container_width=True); download_df(cf,"tea_cashflow.csv")
        st.subheader("Sensitivity analysis"); c=st.columns(4); pl=c[0].number_input("Selling-value low (%)",-80.0,0.0,-20.0); ph=c[1].number_input("Selling-value high (%)",0.0,200.0,20.0); vl=c[2].number_input("Variable-cost low (%)",-80.0,0.0,-20.0); vh=c[3].number_input("Variable-cost high (%)",0.0,200.0,20.0); pg=np.linspace(1+pl/100,1+ph/100,9); vg=np.linspace(1+vl/100,1+vh/100,9); rows=[]
        for pm in pg:
            for vm in vg:
                rr=effective*price*pm; vo=effective*var_cost*vm; ee=rr-(fixed+labor+utilities+maintenance+vo+other_opex); eb=ee-depreciation; tx=max(0.0,eb*tax/100); ff=eb-tx+depreciation; cc=[-total_capex-working_capital]+[ff]*int(years); cc[-1]+=salvage+working_capital; rows.append({"Selling value multiplier":pm,"Variable-cost multiplier":vm,"NPV":sum(v/((1+discount/100)**i) for i,v in enumerate(cc))})
        sens=pd.DataFrame(rows); pivot=sens.pivot(index="Variable-cost multiplier",columns="Selling value multiplier",values="NPV"); st.plotly_chart(px.imshow(pivot,aspect="auto",title="NPV sensitivity: selling value vs variable cost",labels={"x":"Selling value multiplier","y":"Variable-cost multiplier","color":"NPV"}),use_container_width=True)
    else:
        st.subheader("🌍 Life Cycle Assessment (LCA)"); st.write("Build a transparent screening LCA from material, energy, transport and emission flows, normalized to a defined functional unit.")
        with st.expander("1. Goal, scope & functional unit",expanded=True):
            c1,c2=st.columns(2)
            with c1: goal=st.text_area("Goal","Compare the environmental burden of two process scenarios."); fu=st.text_input("Functional unit","1 kg product / 1 m³ treated wastewater"); boundary=st.selectbox("System boundary",["Gate-to-gate","Cradle-to-gate","Cradle-to-grave","Custom"])
            with c2: name=st.text_input("Assessment name","SciMantra screening LCA"); reference=st.number_input("Reference output for inventory",min_value=0.000001,value=1000.0); st.caption("Enter inventory quantities on a consistent reference basis; the tool normalizes results to one functional unit.")
        st.subheader("2. Life-cycle inventory")
        default=pd.DataFrame([{ "Flow":"Electricity","Quantity":100.0,"Unit":"kWh","Emission_factor":0.7,"EF_unit":"kg CO2e/unit","Stage":"Operation","Category":"Energy"},{"Flow":"Water","Quantity":2.0,"Unit":"m³","Emission_factor":0.3,"EF_unit":"kg CO2e/unit","Stage":"Operation","Category":"Water"},{"Flow":"Chemical","Quantity":5.0,"Unit":"kg","Emission_factor":2.0,"EF_unit":"kg CO2e/unit","Stage":"Upstream","Category":"Material"},{"Flow":"Transport","Quantity":50.0,"Unit":"tkm","Emission_factor":0.1,"EF_unit":"kg CO2e/unit","Stage":"Transport","Category":"Transport"}])
        inv=st.data_editor(default,num_rows="dynamic",use_container_width=True,key="lca_inventory").copy()
        for col in ["Quantity","Emission_factor"]: inv[col]=pd.to_numeric(inv[col],errors="coerce").fillna(0.0)
        inv["CO2e_kg"]=inv["Quantity"]*inv["Emission_factor"]; inv["CO2e_per_FU"]=inv["CO2e_kg"]/reference; total=inv["CO2e_kg"].sum(); per_fu=total/reference
        st.subheader("3. Results"); c=st.columns(2); c[0].metric("Total inventory GHG burden",f"{total:,.3f} kg CO₂e"); c[1].metric("GHG intensity",f"{per_fu:,.6f} kg CO₂e / functional unit")
        c1,c2=st.columns(2); stage=inv.groupby("Stage",as_index=False)["CO2e_kg"].sum().sort_values("CO2e_kg",ascending=False); category=inv.groupby("Category",as_index=False)["CO2e_kg"].sum().sort_values("CO2e_kg",ascending=False); c1.plotly_chart(px.bar(stage,x="Stage",y="CO2e_kg",title="Contribution by life-cycle stage"),use_container_width=True); c2.plotly_chart(px.bar(category,x="Category",y="CO2e_kg",title="Contribution by inventory category"),use_container_width=True); st.dataframe(inv,use_container_width=True); download_df(inv,"lca_inventory_results.csv")
        st.subheader("4. Scenario comparison")
        scenarios=st.data_editor(pd.DataFrame([{ "Scenario":"Baseline","Total_CO2e_kg":total},{"Scenario":"Alternative","Total_CO2e_kg":total*0.8}]),num_rows="dynamic",use_container_width=True,key="lca_scenarios").copy(); scenarios["Total_CO2e_kg"]=pd.to_numeric(scenarios["Total_CO2e_kg"],errors="coerce"); scenarios["kg_CO2e_per_FU"]=scenarios["Total_CO2e_kg"]/reference; base=scenarios.loc[scenarios["Scenario"]=="Baseline","Total_CO2e_kg"]; baseval=float(base.iloc[0]) if len(base) else float(total); scenarios["Reduction_vs_baseline_%"]=(baseval-scenarios["Total_CO2e_kg"])/baseval*100 if baseval else np.nan; st.dataframe(scenarios,use_container_width=True); st.plotly_chart(px.bar(scenarios,x="Scenario",y="kg_CO2e_per_FU",title="Scenario GHG intensity"),use_container_width=True); download_df(scenarios,"lca_scenario_comparison.csv")
        st.subheader("5. Sensitivity analysis")
        if len(inv):
            flow=st.selectbox("Flow to vary",inv["Flow"].tolist()); base_row=inv.loc[inv["Flow"]==flow].iloc[0]; factors=np.linspace(0.5,1.5,11); sens=pd.DataFrame({"Multiplier":factors,"Total_CO2e_kg":[total-base_row["CO2e_kg"]+base_row["CO2e_kg"]*f for f in factors]}); sens["kg_CO2e_per_FU"]=sens["Total_CO2e_kg"]/reference; st.plotly_chart(px.line(sens,x="Multiplier",y="kg_CO2e_per_FU",markers=True,title=f"LCA sensitivity: {flow}"),use_container_width=True); download_df(sens,"lca_sensitivity.csv")
        st.warning("Screening-level LCA: emission factors, allocation, data quality, cut-offs and impact categories must be documented. This is not a substitute for a full ISO-conformant LCA or a recognized multi-impact database.")

st.divider()
st.caption("SciMantra Research Tools • Educational/research aid. Verify calculations against the standard method, SOP, instrument protocol, data source and applicable scientific guidelines before use.")
