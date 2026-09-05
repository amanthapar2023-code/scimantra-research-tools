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
    "🌱 Environmental Biotechnology", "📈 Data Analyzer", "🔬 Research Tools", "🌍 TEA & LCA"
])

def download_df(df, filename="scimantra_results.csv"):
    st.download_button("⬇️ Download CSV", df.to_csv(index=False).encode("utf-8"), filename, "text/csv")

def irr_roots(cashflows, max_rate=1000.0):
    cf = np.asarray(cashflows, dtype=float)
    if len(cf) < 2 or not (np.any(cf > 0) and np.any(cf < 0)):
        return []
    def f(rate):
        return sum(v / ((1 + rate) ** i) for i, v in enumerate(cf))
    grid = np.unique(np.concatenate(([-0.9999, -0.99, -0.9, -0.5, -0.1, 0.0], np.geomspace(1e-8, max_rate, 300))))
    vals = [f(float(r)) for r in grid]
    roots = []
    for i in range(len(grid)-1):
        a,b = float(grid[i]),float(grid[i+1]); fa,fb=vals[i],vals[i+1]
        if not (np.isfinite(fa) and np.isfinite(fb)): continue
        if fa == 0: roots.append(a)
        elif fa*fb < 0:
            try:
                root=brentq(f,a,b)
                if not roots or abs(root-roots[-1])>1e-6: roots.append(root)
            except Exception: pass
    return roots

def payback(cashflows, discounted=False, rate=0.0):
    cumulative=0.0
    for i,v in enumerate(cashflows):
        pv=v/((1+rate)**i) if discounted else v
        previous=cumulative; cumulative += pv
        if cumulative >= 0 and i>0:
            return float(i) if pv==0 else (i-1)+max(0.0,min(1.0,-previous/pv))
    return np.nan

def npv_of(cf, rate):
    return sum(v/((1+rate)**i) for i,v in enumerate(cf))

if section == "🏠 Dashboard":
    st.subheader("Research tools in one place")
    cols=st.columns(3)
    cards=[
        ("🧪 Laboratory","Molarity, dilution, CFU/mL, BOD, COD, biomass and growth calculations."),
        ("📊 Statistics","Mean, SD, SEM, CV, t-test, ANOVA, correlation and regression."),
        ("🌱 Environment","Removal efficiency, loading, EBRT and H₂S analysis."),
        ("📈 Data Analyzer","Upload Excel/CSV files, summarize replicates and create interactive graphs."),
        ("🔬 Research","Standard curves, experimental design and manuscript checklists."),
        ("🌍 TEA & LCA","Screen process economics, NPV, IRR, life-cycle inventory and CO₂e intensity."),
    ]
    for i,(title,desc) in enumerate(cards):
        with cols[i%3]: st.markdown(f'<div class="tool-card"><h3>{title}</h3><p>{desc}</p></div>',unsafe_allow_html=True)
    st.info("Tip: start with Data Analyzer for an Excel/CSV dataset, or TEA & LCA for process sustainability evaluation.")

elif section == "🧪 Laboratory Calculators":
    tool=st.selectbox("Calculator",["Molarity","Dilution (C₁V₁ = C₂V₂)","% Solution","Normality","CFU/mL","Biomass concentration","Growth rate","Specific growth rate","BOD","COD"])
    if tool=="Molarity":
        st.subheader("Molarity Calculator"); mass=st.number_input("Mass of solute (g)",min_value=0.0,value=1.0); mw=st.number_input("Molecular weight (g/mol)",min_value=1e-6,value=58.44); vol=st.number_input("Final volume (L)",min_value=1e-6,value=1.0); st.metric("Molarity",f"{mass/mw/vol:.6g} mol/L")
    elif tool=="Dilution (C₁V₁ = C₂V₂)":
        st.subheader("Dilution Calculator"); c1=st.number_input("C₁ (stock concentration)",min_value=0.0,value=100.0); c2=st.number_input("C₂ (desired concentration)",min_value=1e-6,value=10.0); v2=st.number_input("V₂ (final volume)",min_value=1e-6,value=100.0); v1=c2*v2/c1 if c1 else 0; st.metric("Stock volume V₁",f"{v1:.4g}"); st.metric("Diluent volume",f"{v2-v1:.4g}")
    elif tool=="% Solution":
        st.subheader("Percentage Solution"); st.selectbox("Type",["w/v (% g per 100 mL)","w/w (% g per 100 g)","v/v (% mL per 100 mL)"]); amount=st.number_input("Solute amount",min_value=0.0,value=5.0); total=st.number_input("Total amount/volume",min_value=1e-6,value=100.0); st.metric("Percentage",f"{amount/total*100:.4g}%")
    elif tool=="Normality":
        st.subheader("Normality Calculator"); m=st.number_input("Molarity (mol/L)",min_value=0.0,value=1.0); n=st.number_input("n-factor / equivalent factor",min_value=1e-6,value=1.0); st.metric("Normality",f"{m*n:.6g} N")
    elif tool=="CFU/mL":
        st.subheader("CFU/mL Calculator"); colonies=st.number_input("Colonies counted",min_value=0.0,value=125.0); dilution=st.number_input("Reciprocal dilution",min_value=1.0,value=100000.0); plated=st.number_input("Volume plated (mL)",min_value=1e-6,value=0.1); st.metric("CFU/mL",f"{colonies*dilution/plated:.6g}")
    elif tool=="Biomass concentration":
        st.subheader("Biomass Concentration"); dry=st.number_input("Dry biomass (g)",min_value=0.0,value=1.0); v=st.number_input("Culture volume (L)",min_value=1e-6,value=1.0); st.metric("Biomass",f"{dry/v:.6g} g/L")
    elif tool=="Growth rate":
        st.subheader("Average Growth Rate"); x1=st.number_input("Measurement 1",value=0.1); x2=st.number_input("Measurement 2",value=0.8); t1=st.number_input("Time 1",value=0.0); t2=st.number_input("Time 2",value=10.0); st.metric("Growth rate",f"{(x2-x1)/(t2-t1):.6g} units/time" if t2!=t1 else "N/A")
    elif tool=="Specific growth rate":
        st.subheader("Specific Growth Rate"); x1=st.number_input("X₁",min_value=1e-6,value=0.1); x2=st.number_input("X₂",min_value=1e-6,value=0.8); dt=st.number_input("Δt",min_value=1e-6,value=10.0); st.metric("μ",f"{math.log(x2/x1)/dt:.6g} time⁻¹")
    elif tool=="BOD":
        st.subheader("BOD Calculator"); initial=st.number_input("Initial DO (mg/L)",value=8.0); final=st.number_input("Final DO (mg/L)",value=3.0); sample=st.number_input("Sample volume (mL)",min_value=1e-6,value=15.0); bottle=st.number_input("Bottle volume (mL)",min_value=1e-6,value=300.0); st.metric("Approx. BOD₅",f"{(initial-final)*bottle/sample:.6g} mg/L"); st.caption("Apply appropriate standard-method seed, dilution-water and blank corrections where applicable.")
    elif tool=="COD":
        st.subheader("COD Calculator"); a=st.number_input("Blank titration A (mL)",value=20.0); b=st.number_input("Sample titration B (mL)",value=12.0); normality=st.number_input("Titrant normality",min_value=1e-6,value=0.1); volume=st.number_input("Sample volume (mL)",min_value=1e-6,value=10.0); st.metric("COD",f"{(a-b)*normality*8000/volume:.6g} mg/L"); st.caption("Verify the reagent-specific equation and laboratory method.")

elif section == "📊 Statistics":
    tool=st.selectbox("Statistical tool",["Descriptive statistics","t-Test","One-way ANOVA","Correlation","Linear regression"]); uploaded=st.file_uploader("Upload CSV/Excel (optional)",type=["csv","xlsx"]); df=None
    if uploaded: df=pd.read_csv(uploaded) if uploaded.name.endswith(".csv") else pd.read_excel(uploaded); st.dataframe(df.head(20),use_container_width=True)
    if tool=="Descriptive statistics":
        if df is not None:
            numeric=df.select_dtypes(include=np.number); result=numeric.describe().T; result["SEM"]=numeric.sem(); result["CV_%"]=numeric.std(ddof=1)/numeric.mean()*100; st.dataframe(result,use_container_width=True); download_df(result.reset_index().rename(columns={"index":"Variable"}),"descriptive_statistics.csv")
        else:
            vals=st.text_area("Enter values separated by commas","1,2,3,4,5,6")
            try:
                x=np.array([float(v.strip()) for v in vals.split(",") if v.strip()]); c=st.columns(4); c[0].metric("Mean",f"{x.mean():.5g}"); c[1].metric("SD",f"{x.std(ddof=1):.5g}" if len(x)>1 else "NA"); c[2].metric("SEM",f"{stats.sem(x):.5g}" if len(x)>1 else "NA"); c[3].metric("CV %",f"{x.std(ddof=1)/x.mean()*100:.5g}" if len(x)>1 and x.mean()!=0 else "NA")
            except Exception: st.error("Please enter numeric values.")
    elif tool=="t-Test":
        a=st.text_area("Group A","1,2,3,4,5"); b=st.text_area("Group B","2,3,4,5,6")
        try: x=[float(v) for v in a.split(",") if v.strip()]; y=[float(v) for v in b.split(",") if v.strip()]; r=stats.ttest_ind(x,y,equal_var=False); st.metric("t statistic",f"{r.statistic:.6g}"); st.metric("p-value",f"{r.pvalue:.6g}"); st.caption("Welch's independent two-sample t-test.")
        except Exception: st.warning("Enter two comma-separated numeric groups.")
    elif tool=="One-way ANOVA":
        txt=st.text_area("Groups (one group per line)","1,2,3\n2,3,4\n5,6,7")
        try: groups=[[float(v) for v in line.split(",") if v.strip()] for line in txt.splitlines() if line.strip()]; r=stats.f_oneway(*groups); st.metric("F statistic",f"{r.statistic:.6g}"); st.metric("p-value",f"{r.pvalue:.6g}")
        except Exception: st.warning("Enter numeric groups, one group per line.")
    elif tool=="Correlation":
        x=st.text_area("X values","1,2,3,4,5"); y=st.text_area("Y values","2,4,5,8,10"); method=st.selectbox("Method",["Pearson","Spearman"])
        try: xx=np.array([float(v) for v in x.split(",") if v.strip()]); yy=np.array([float(v) for v in y.split(",") if v.strip()]); r=stats.pearsonr(xx,yy) if method=="Pearson" else stats.spearmanr(xx,yy); st.metric("Correlation coefficient",f"{r.statistic:.6g}"); st.metric("p-value",f"{r.pvalue:.6g}")
        except Exception: st.warning("Enter equal-length numeric arrays.")
    elif tool=="Linear regression":
        x=st.text_area("X values","1,2,3,4,5"); y=st.text_area("Y values","2,4,5,8,10")
        try: xx=np.array([float(v) for v in x.split(",") if v.strip()]); yy=np.array([float(v) for v in y.split(",") if v.strip()]); r=stats.linregress(xx,yy); c=st.columns(4); c[0].metric("Slope",f"{r.slope:.6g}"); c[1].metric("Intercept",f"{r.intercept:.6g}"); c[2].metric("R²",f"{r.rvalue**2:.6g}"); c[3].metric("p-value",f"{r.pvalue:.6g}"); order=np.argsort(xx); st.plotly_chart(go.Figure([go.Scatter(x=xx,y=yy,mode="markers",name="Data"),go.Scatter(x=xx[order],y=r.intercept+r.slope*xx[order],mode="lines",name="Fit")]),use_container_width=True)
        except Exception: st.warning("Enter equal-length numeric arrays.")

elif section == "🌱 Environmental Biotechnology":
    tool=st.selectbox("Environmental tool",["Removal efficiency","Loading rate","EBRT","H₂S removal","Concentration conversion"])
    if tool=="Removal efficiency":
        cin=st.number_input("Influent concentration",value=100.0); cout=st.number_input("Effluent concentration",value=20.0); st.metric("Removal efficiency",f"{(cin-cout)/cin*100:.4g}%" if cin else "N/A")
    elif tool=="Loading rate":
        concentration=st.number_input("Concentration",value=100.0,min_value=0.0); flow=st.number_input("Flow rate",value=1.0,min_value=1e-6); reactor=st.number_input("Reactor/bed volume",value=1.0,min_value=1e-6); st.metric("Volumetric loading",f"{concentration*flow/reactor:.6g}"); st.caption("Confirm unit consistency.")
    elif tool=="EBRT":
        volume=st.number_input("Bioreactor/bed volume",value=1.0,min_value=1e-6); flow=st.number_input("Gas/liquid flow rate",value=1.0,min_value=1e-6); st.metric("EBRT",f"{volume/flow:.6g} time units")
    elif tool=="H₂S removal":
        cin=st.number_input("H₂S inlet concentration",value=500.0); cout=st.number_input("H₂S outlet concentration",value=50.0); flow=st.number_input("Gas flow rate",value=1.0,min_value=1e-6); st.metric("Removal",f"{(cin-cout)/cin*100:.4g}%" if cin else "N/A"); st.metric("Removed concentration × flow",f"{(cin-cout)*flow:.6g}")
    elif tool=="Concentration conversion":
        value=st.number_input("Value",value=1.0); from_unit=st.selectbox("From",["mg/L","µg/L","g/L","ppm (water, approx.)"]); to_unit=st.selectbox("To",["mg/L","µg/L","g/L","ppm (water, approx.)"]); factors={"µg/L":.001,"mg/L":1.,"g/L":1000.,"ppm (water, approx.)":1.}; st.metric("Converted value",f"{value*factors[from_unit]/factors[to_unit]:.6g} {to_unit}")

elif section == "📈 Data Analyzer":
    st.subheader("Upload and explore your research data"); uploaded=st.file_uploader("Upload Excel or CSV",type=["xlsx","csv"])
    if not uploaded: st.info("Upload a dataset to begin. Recommended structure: one observation per row, with columns such as Group, Replicate, Time, Concentration.")
    else:
        df=pd.read_csv(uploaded) if uploaded.name.endswith(".csv") else pd.read_excel(uploaded); st.success(f"Loaded {len(df):,} rows × {len(df.columns):,} columns"); st.dataframe(df.head(100),use_container_width=True); numeric=df.select_dtypes(include=np.number).columns.tolist(); tabs=st.tabs(["Summary","Plot","Correlation","Replicates"])
        with tabs[0]: st.dataframe(df[numeric].describe().T if numeric else df.describe(include="all").T,use_container_width=True)
        with tabs[1]:
            if numeric:
                y=st.selectbox("Y-axis",numeric); x_options=[c for c in df.columns if c!=y]; x=st.selectbox("X-axis",x_options) if x_options else None; color=st.selectbox("Group/color (optional)",["None"]+[c for c in df.columns if c not in [x,y]])
                if x:
                    fig=px.scatter(df,x=x,y=y,color=None if color=="None" else color,trendline="ols"); st.plotly_chart(fig,use_container_width=True); st.download_button("⬇️ Download interactive plot HTML",fig.to_html(include_plotlyjs="cdn").encode(),"scimantra_plot.html")
        with tabs[2]:
            if len(numeric)>=2: st.plotly_chart(px.imshow(df[numeric].corr(numeric_only=True),text_auto=".2f",aspect="auto",title="Correlation heatmap"),use_container_width=True)
            else: st.info("Need at least two numeric columns.")
        with tabs[3]:
            rep_col=st.selectbox("Replicate column",["None"]+list(df.columns)); value_col=st.selectbox("Measurement column",numeric if numeric else ["None"])
            if rep_col!="None" and value_col!="None": summary=df.groupby(rep_col)[value_col].agg(["count","mean","std","sem","min","max"]).reset_index(); st.dataframe(summary,use_container_width=True); download_df(summary,"replicate_summary.csv")

elif section == "🔬 Research Tools":
    tool=st.selectbox("Research utility",["Standard curve","Experimental design planner","Manuscript checklist"])
    if tool=="Standard curve":
        st.subheader("Standard Curve Generator"); x_text=st.text_area("Known concentrations","0,10,20,40,80,100"); y_text=st.text_area("Measured response","0.02,0.11,0.21,0.42,0.83,1.02"); unknown=st.number_input("Unknown response to estimate",value=.55)
        try:
            x=np.array([float(v) for v in x_text.split(",") if v.strip()]); y=np.array([float(v) for v in y_text.split(",") if v.strip()]); fit=stats.linregress(x,y); est=(unknown-fit.intercept)/fit.slope; c=st.columns(4); c[0].metric("Slope",f"{fit.slope:.6g}"); c[1].metric("Intercept",f"{fit.intercept:.6g}"); c[2].metric("R²",f"{fit.rvalue**2:.6g}"); c[3].metric("Estimated unknown",f"{est:.6g}"); xx=np.linspace(x.min(),x.max(),100); st.plotly_chart(go.Figure([go.Scatter(x=x,y=y,mode="markers",name="Standards"),go.Scatter(x=xx,y=fit.intercept+fit.slope*xx,mode="lines",name="Regression")]),use_container_width=True)
        except Exception: st.warning("Enter equal-length numeric arrays.")
    elif tool=="Experimental design planner":
        st.subheader("Simple Experimental Design Planner"); groups=st.number_input("Number of experimental groups",1,50,3); reps=st.number_input("Biological/independent replicates per group",1,100,3); tech=st.number_input("Technical measurements per replicate",1,20,1); total=int(groups*reps*tech); st.metric("Total measurements",total); plan=pd.DataFrame([[f"Group {g}",f"R{r}",f"T{t}"] for g in range(1,int(groups)+1) for r in range(1,int(reps)+1) for t in range(1,int(tech)+1)],columns=["Group","Replicate","Technical"]); st.dataframe(plan,use_container_width=True); download_df(plan,"experimental_design_plan.csv")
    else:
        st.subheader("Research Manuscript Checklist"); items=["Research question/objective is clearly stated","Appropriate controls are described","Replicates are clearly defined","Methods contain enough detail for reproducibility","Statistical tests match the experimental design","Raw/processed data are organized","Figures have clear labels and units","Error bars are defined","p-values/effect sizes are reported appropriately","Results are separated from interpretation","Discussion connects findings to literature","Limitations are acknowledged","References are checked","Abstract matches the final results"]; done=sum(st.checkbox(x) for x in items); st.progress(done/len(items)); st.write(f"Completed: **{done}/{len(items)}**")

elif section == "🌍 TEA & LCA":
    st.header("🌍 Sustainability & Process Evaluation")
    st.caption("Techno-Economic Analysis (TEA) and Life Cycle Assessment (LCA) — transparent research decision-support tools")
    st.info("Screening-level models only. Define system boundary, functional unit, currency, year, data sources and assumptions before using results in a publication, feasibility study or investment decision.")
    analysis=st.radio("Choose analysis",["💰 Techno-Economic Analysis (TEA)","🌍 Life Cycle Assessment (LCA)"],horizontal=True)
    if analysis.startswith("💰"):
        st.subheader("💰 Techno-Economic Analysis (TEA)")
        with st.expander("1. Project & production assumptions",expanded=True):
            c1,c2,c3=st.columns(3)
            with c1:
                currency=st.text_input("Currency symbol","₹"); years=st.number_input("Project life (years)",1,50,10); output=st.number_input("Nameplate annual output / treatment capacity",min_value=1e-6,value=1000.)
            with c2:
                unit=st.text_input("Output unit","kg or m³"); price=st.number_input("Selling value / avoided treatment cost per unit",min_value=0.,value=100.); cap_factor=st.number_input("Capacity factor (%)",0.,100.,90.)
            with c3:
                discount=st.number_input("Discount rate (%)",0.,100.,10.); tax=st.number_input("Tax rate (%)",0.,100.,25.); salvage_pct=st.number_input("Salvage value (% of depreciable CAPEX)",0.,100.,5.)
        with st.expander("2. Capital expenditure (CAPEX)",expanded=True):
            c1,c2,c3=st.columns(3)
            with c1: equipment=st.number_input("Equipment & process units",min_value=0.,value=500000.); installation=st.number_input("Installation & civil works",min_value=0.,value=150000.)
            with c2: engineering=st.number_input("Engineering / commissioning",min_value=0.,value=75000.); contingency_pct=st.number_input("Contingency (%)",0.,100.,10.)
            with c3: other_capex=st.number_input("Other CAPEX",min_value=0.,value=0.); working_capital=st.number_input("Initial working capital",min_value=0.,value=50000.)
        direct_capex=equipment+installation+engineering+other_capex; contingency=direct_capex*contingency_pct/100; total_capex=direct_capex+contingency; initial_investment=total_capex+working_capital
        with st.expander("3. Annual operating expenditure (OPEX)",expanded=True):
            c1,c2,c3=st.columns(3)
            with c1: fixed=st.number_input("Fixed OPEX / year",min_value=0.,value=100000.); labor=st.number_input("Labor / year",min_value=0.,value=120000.)
            with c2: utilities=st.number_input("Utilities / year",min_value=0.,value=80000.); maintenance_pct=st.number_input("Maintenance (% of CAPEX/year)",0.,100.,4.)
            with c3: variable=st.number_input(f"Variable cost / {unit}",min_value=0.,value=20.); other=st.number_input("Other OPEX / year",min_value=0.,value=0.)
        effective=output*cap_factor/100; maintenance=total_capex*maintenance_pct/100; fixed_cash=fixed+labor+utilities+maintenance+other; variable_opex=effective*variable; revenue=effective*price; annual_opex=fixed_cash+variable_opex; ebitda=revenue-annual_opex; depreciation=total_capex/years; ebit=ebitda-depreciation; tax_exp=max(0.,ebit*tax/100); fcf=ebit-tax_exp+depreciation; salvage=total_capex*salvage_pct/100
        cashflows=[-initial_investment]+[fcf]*int(years); cashflows[-1]+=salvage+working_capital; year_arr=np.arange(int(years)+1); disc_cf=[cashflows[i]/((1+discount/100)**i) for i in year_arr]; npv=sum(disc_cf); roots=irr_roots(cashflows); simple_pb=payback(cashflows); discounted_pb=payback(cashflows,True,discount/100)
        contribution=price-variable; cash_be=variable+fixed_cash/effective if effective else np.nan; accounting_be=variable+(fixed_cash+depreciation)/effective if effective else np.nan; be_volume=fixed_cash/contribution if contribution>0 else np.nan; roi=((sum(cashflows[1:])-initial_investment)/initial_investment*100) if initial_investment else np.nan; pi=sum(disc_cf[1:])/initial_investment if initial_investment else np.nan
        def npv_price(p):
            ebitda_x=effective*p-fixed_cash-effective*variable; ebit_x=ebitda_x-depreciation; tax_x=max(0.,ebit_x*tax/100); fcf_x=ebit_x-tax_x+depreciation; cf=[-initial_investment]+[fcf_x]*int(years); cf[-1]+=salvage+working_capital; return npv_of(cf,discount/100)
        min_price=np.nan; hi=max(1.,price*10+1.)
        if npv_price(0)<=0<=npv_price(hi):
            try: min_price=brentq(npv_price,0,hi)
            except Exception: pass
        if npv > 0: tea_status="🟢 Economically attractive"
        elif npv >= -0.1*initial_investment: tea_status="🟡 Borderline / needs optimization"
        else: tea_status="🔴 Not economically viable under current assumptions"
        st.subheader("Key TEA results"); c=st.columns(6); c[0].metric("Total CAPEX",f"{currency}{total_capex:,.0f}"); c[1].metric("Initial investment",f"{currency}{initial_investment:,.0f}"); c[2].metric("Annual revenue",f"{currency}{revenue:,.0f}"); c[3].metric("Annual OPEX",f"{currency}{annual_opex:,.0f}"); c[4].metric("Annual FCF",f"{currency}{fcf:,.0f}"); c[5].metric("NPV",f"{currency}{npv:,.0f}")
        c=st.columns(5); c[0].metric("IRR",f"{roots[0]*100:.2f}%" if len(roots)==1 else (f"Multiple ({len(roots)})" if len(roots)>1 else "N/A")); c[1].metric("Simple payback",f"{simple_pb:.2f} years" if np.isfinite(simple_pb) else "Not reached"); c[2].metric("Discounted payback",f"{discounted_pb:.2f} years" if np.isfinite(discounted_pb) else "Not reached"); c[3].metric("Lifetime ROI",f"{roi:.2f}%" if np.isfinite(roi) else "N/A"); c[4].metric("Profitability index",f"{pi:.3f}" if np.isfinite(pi) else "N/A")
        st.subheader("Decision screen"); st.warning(tea_status) if tea_status.startswith("🔴") else (st.info(tea_status) if tea_status.startswith("🟡") else st.success(tea_status)); st.caption("Decision screen is a screening aid, not an investment recommendation. Formal TEA should include project-specific financing, escalation, depreciation, tax, working-capital, replacement and decommissioning assumptions.")
        st.subheader("Break-even & investment indicators"); c=st.columns(4); c[0].metric("Cash break-even value / unit",f"{currency}{cash_be:,.2f}" if np.isfinite(cash_be) else "N/A"); c[1].metric("Accounting break-even value / unit",f"{currency}{accounting_be:,.2f}" if np.isfinite(accounting_be) else "N/A"); c[2].metric("Break-even annual volume",f"{be_volume:,.2f}" if np.isfinite(be_volume) else "N/A"); c[3].metric("NPV-zero minimum selling value",f"{currency}{min_price:,.2f}" if np.isfinite(min_price) else "N/A")
        st.caption("Cash break-even excludes depreciation; accounting break-even includes depreciation. Minimum selling value is the unit value required for NPV ≈ 0 at the selected discount rate.")
        cf_df=pd.DataFrame({"Year":year_arr,"Revenue":[0.]+[revenue]*int(years),"OPEX":[0.]+[annual_opex]*int(years),"EBITDA":[0.]+[ebitda]*int(years),"Tax":[0.]+[tax_exp]*int(years),"Free cash flow":cashflows,"Discounted cash flow":disc_cf,"Cumulative cash flow":np.cumsum(cashflows),"Cumulative discounted cash flow":np.cumsum(disc_cf)})
        st.subheader("Cash-flow profile"); st.plotly_chart(px.line(cf_df,x="Year",y=["Cumulative cash flow","Cumulative discounted cash flow"],markers=True,title="Cumulative project cash flow"),use_container_width=True); st.dataframe(cf_df,use_container_width=True); download_df(cf_df,"tea_cashflow.csv")
        st.subheader("Scenario analysis"); rows=[]
        for name,pm,vm in [("Conservative",.8,1.2),("Base",1.,1.),("Optimistic",1.2,.8)]:
            p=price*pm; vc=variable*vm; rev=effective*p; op=fixed_cash+effective*vc; e=rev-op-depreciation; tx=max(0.,e*tax/100); f=e-tx+depreciation; cf=[-initial_investment]+[f]*int(years); cf[-1]+=salvage+working_capital; rr=irr_roots(cf); rows.append({"Scenario":name,"Selling value / unit":p,"Variable cost / unit":vc,"Annual revenue":rev,"Annual OPEX":op,"Annual FCF":f,"NPV":npv_of(cf,discount/100),"IRR_%":rr[0]*100 if len(rr)==1 else np.nan})
        scenario_df=pd.DataFrame(rows); st.dataframe(scenario_df,use_container_width=True); st.plotly_chart(px.bar(scenario_df,x="Scenario",y="NPV",title="Scenario NPV comparison"),use_container_width=True); download_df(scenario_df,"tea_scenario_analysis.csv")
        st.subheader("Sensitivity analysis"); c1,c2,c3=st.columns(3); price_low=c1.number_input("Selling-value low (%)",-80.,0.,-20.); price_high=c2.number_input("Selling-value high (%)",0.,200.,20.); var_low=c3.number_input("Variable-cost low (%)",-80.,0.,-20.); var_high=st.number_input("Variable-cost high (%)",0.,200.,20.); rows=[]
        for pm in np.linspace(1+price_low/100,1+price_high/100,9):
            for vm in np.linspace(1+var_low/100,1+var_high/100,9):
                p=price*pm; vc=variable*vm; rev=effective*p; op=fixed_cash+effective*vc; e=rev-op-depreciation; tx=max(0.,e*tax/100); f=e-tx+depreciation; cf=[-initial_investment]+[f]*int(years); cf[-1]+=salvage+working_capital; rows.append({"Selling value multiplier":pm,"Variable-cost multiplier":vm,"NPV":npv_of(cf,discount/100)})
        sens=pd.DataFrame(rows); pivot=sens.pivot(index="Variable-cost multiplier",columns="Selling value multiplier",values="NPV"); st.plotly_chart(px.imshow(pivot,aspect="auto",title="NPV sensitivity: selling value vs variable cost",labels={"x":"Selling value multiplier","y":"Variable-cost multiplier","color":"NPV"}),use_container_width=True)
        with st.expander("TEA equations & interpretation"):
            st.markdown("**NPV > 0** indicates positive value at the selected discount rate under the stated assumptions. **IRR** is reported only when a unique root is found; multiple roots are flagged. **Lifetime ROI** is cumulative project cash returned relative to initial investment; it is not a standardized accounting ROI definition. Break-even outputs distinguish cash and accounting definitions.")
    else:
        st.subheader("🌍 Life Cycle Assessment (LCA)")
        st.write("Build a transparent screening LCA from material, energy, transport and emission flows, normalized to one clearly defined functional unit.")
        with st.expander("1. Goal, scope & functional unit",expanded=True):
            c1,c2=st.columns(2)
            with c1:
                goal=st.text_area("Goal","Compare the environmental burden of two process scenarios.")
                functional_unit=st.text_input("Functional unit (one service/product basis)","1 kg product")
                reference_unit=st.text_input("Reference flow / output unit","kg product")
                boundary=st.selectbox("System boundary",["Gate-to-gate","Cradle-to-gate","Cradle-to-grave","Custom"])
            with c2:
                assessment=st.text_input("Assessment name","SciMantra screening LCA")
                reference=st.number_input("Reference flow quantity",min_value=1e-6,value=1000.)
                year_ref=st.number_input("Data/reference year",1900,2100,2026)
                geography=st.text_input("Geography / context","Specify country, region or site")
                technology=st.text_input("Technology / process description","Specify process configuration")
            st.caption(f"Normalization basis: {reference:g} {reference_unit}. Report results per the functional unit **{functional_unit}**; keep the inventory reference flow explicit and consistent.")
        st.subheader("2. Life-cycle inventory")
        default=pd.DataFrame([
            {"Flow":"Electricity","Quantity":100.,"Unit":"kWh","Emission_factor":.7,"EF_unit":"kg CO2e/unit","Stage":"Operation","Category":"Energy","Source":"Example assumption","Geography":"Specify","Data_year":2026,"Uncertainty_%":0.},
            {"Flow":"Water","Quantity":2.,"Unit":"m³","Emission_factor":.3,"EF_unit":"kg CO2e/unit","Stage":"Operation","Category":"Water","Source":"Example assumption","Geography":"Specify","Data_year":2026,"Uncertainty_%":0.},
            {"Flow":"Chemical","Quantity":5.,"Unit":"kg","Emission_factor":2.,"EF_unit":"kg CO2e/unit","Stage":"Upstream","Category":"Material","Source":"Example assumption","Geography":"Specify","Data_year":2026,"Uncertainty_%":0.},
            {"Flow":"Transport","Quantity":50.,"Unit":"tkm","Emission_factor":.1,"EF_unit":"kg CO2e/unit","Stage":"Transport","Category":"Transport","Source":"Example assumption","Geography":"Specify","Data_year":2026,"Uncertainty_%":0.},
        ])
        edited=st.data_editor(default,num_rows="dynamic",use_container_width=True,key="lca_inventory_v2"); inv=edited.copy()
        for col in ["Quantity","Emission_factor","Data_year","Uncertainty_%"]: inv[col]=pd.to_numeric(inv[col],errors="coerce")
        invalid=int(inv[["Quantity","Emission_factor"]].isna().any(axis=1).sum()); inv[["Quantity","Emission_factor"]]=inv[["Quantity","Emission_factor"]].fillna(0.)
        inv["Uncertainty_%"]=inv["Uncertainty_%"].fillna(0.).clip(lower=0.)
        inv["Data_year"]=inv["Data_year"].fillna(year_ref)
        if invalid: st.warning(f"{invalid} inventory row(s) contained non-numeric quantity/emission-factor values; those cells were treated as zero.")
        inv["CO2e_kg"]=inv["Quantity"]*inv["Emission_factor"]; inv["CO2e_per_reference_output"]=inv["CO2e_kg"]/reference
        inv["Uncertainty_abs_kgCO2e"]=inv["CO2e_kg"].abs()*inv["Uncertainty_%"]/100
        total=float(inv["CO2e_kg"].sum()); per_ref=total/reference; combined_unc=float(np.sqrt(np.square(inv["Uncertainty_abs_kgCO2e"]).sum()))
        lower=max(0.,total-combined_unc); upper=total+combined_unc
        st.subheader("3. Results"); c1,c2,c3=st.columns(3); c1.metric("Total inventory GHG burden",f"{total:,.3f} kg CO₂e"); c2.metric("GHG intensity",f"{per_ref:,.6f} kg CO₂e / {functional_unit}"); c3.metric("Approx. uncertainty range",f"{lower:,.3f}–{upper:,.3f} kg CO₂e")
        st.caption(f"Functional unit: **{functional_unit}**. Reference flow: {reference:g} {reference_unit}. The uncertainty range is an approximate independent-error screen based only on user-entered row uncertainties; it is not a Monte Carlo confidence interval.")
        stage=inv.groupby("Stage",as_index=False)["CO2e_kg"].sum().sort_values("CO2e_kg",ascending=False); category=inv.groupby("Category",as_index=False)["CO2e_kg"].sum().sort_values("CO2e_kg",ascending=False); c1,c2=st.columns(2)
        with c1: st.plotly_chart(px.bar(stage,x="Stage",y="CO2e_kg",title="Contribution by life-cycle stage"),use_container_width=True)
        with c2: st.plotly_chart(px.bar(category,x="Category",y="CO2e_kg",title="Contribution by inventory category"),use_container_width=True)
        st.dataframe(inv,use_container_width=True); download_df(inv,"lca_inventory_results.csv")
        with st.expander("Data-quality & methodology record"):
            st.write(f"**Assessment:** {assessment}")
            st.write(f"**Goal:** {goal}")
            st.write(f"**Boundary:** {boundary}")
            st.write(f"**Functional unit:** {functional_unit}")
            st.write(f"**Reference flow:** {reference:g} {reference_unit}")
            st.write(f"**Geography/context:** {geography}")
            st.write(f"**Technology/process:** {technology}")
            st.write(f"**Reference year:** {year_ref}")
            st.caption("For formal LCA reporting, document source/database, geography, technology, year, allocation, cut-off criteria and uncertainty for each factor.")
        st.subheader("4. Scenario comparison")
        scenarios=st.data_editor(pd.DataFrame([{"Scenario":"Baseline","Total_CO2e_kg":total},{"Scenario":"Alternative","Total_CO2e_kg":total*.8}]),num_rows="dynamic",use_container_width=True,key="lca_scenarios_v2"); scenarios=scenarios.copy(); scenarios["Total_CO2e_kg"]=pd.to_numeric(scenarios["Total_CO2e_kg"],errors="coerce"); scenarios["kg_CO2e_per_FU"]=scenarios["Total_CO2e_kg"]/reference; baseline=scenarios.loc[scenarios["Scenario"]=="Baseline","Total_CO2e_kg"].dropna(); base=float(baseline.iloc[0]) if len(baseline) else total; scenarios["Reduction_vs_baseline_%"]=(base-scenarios["Total_CO2e_kg"])/base*100 if base else np.nan; st.dataframe(scenarios,use_container_width=True); st.plotly_chart(px.bar(scenarios,x="Scenario",y="kg_CO2e_per_FU",title="Scenario GHG intensity"),use_container_width=True); download_df(scenarios,"lca_scenario_comparison.csv")
        if len(scenarios.dropna(subset=["Total_CO2e_kg"]))>=2:
            alt_rows=scenarios[scenarios["Scenario"]!="Baseline"].dropna(subset=["Total_CO2e_kg"])
            if len(alt_rows):
                best=alt_rows.iloc[0]; reduction=float(best["Reduction_vs_baseline_%"]); st.info(f"Scenario interpretation: **{best['Scenario']}** changes the GHG burden by **{reduction:+.1f}%** versus the baseline. Positive values mean a reduction; negative values mean an increase.")
        st.subheader("5. Sensitivity analysis"); st.caption("Screen the effect of changing one inventory flow while holding all other flows constant.")
        if len(inv):
            flow=st.selectbox("Flow to vary",inv["Flow"].tolist(),key="lca_flow_v2"); base_qty=float(inv.loc[inv["Flow"]==flow,"Quantity"].iloc[0]); low,high=st.slider("Flow quantity range (%)",-80,200,(-50,50),key="lca_range_v2"); rows=[]
            for factor in np.linspace(1+low/100,1+high/100,11):
                changed=inv.copy(); idx=changed.index[changed["Flow"]==flow][0]; changed.loc[idx,"Quantity"]=base_qty*factor; changed["CO2e_kg"]=changed["Quantity"]*changed["Emission_factor"]; t=float(changed["CO2e_kg"].sum()); rows.append({"Quantity multiplier":factor,"Total CO2e (kg)":t,"kg CO2e / FU":t/reference})
            lca_sens=pd.DataFrame(rows); st.plotly_chart(px.line(lca_sens,x="Quantity multiplier",y="kg CO2e / FU",markers=True,title=f"LCA sensitivity: {flow}"),use_container_width=True); st.dataframe(lca_sens,use_container_width=True); download_df(lca_sens,"lca_sensitivity.csv")
            base_contrib=float(inv.loc[inv["Flow"]==flow,"CO2e_kg"].iloc[0]); share=(base_contrib/total*100) if total else 0.; st.info(f"Sensitivity driver: **{flow}** contributes **{share:.1f}%** of baseline GHG burden. Flows with larger contributions generally deserve priority for better emission-factor data and process optimization.")
        with st.expander("6. Research interpretation & reporting notes"):
            st.markdown("**Screening-level result:** this module quantifies greenhouse-gas burden from the entered inventory and emission factors. It is not a substitute for a complete ISO-conformant LCA, verified database, multi-impact assessment, allocation procedure, consequential/attributional choice, uncertainty propagation or critical review. For a thesis or paper, report the functional unit, reference flow, system boundary, geography, technology, data year, source of each emission factor, allocation/cut-off rules and uncertainty method. Use the sensitivity results to justify which parameters require improved primary data.")

st.divider(); st.caption("SciMantra Research Tools • Educational/research aid. Verify calculations against the standard method, SOP, instrument protocol, source data and applicable scientific guidelines before use.")
