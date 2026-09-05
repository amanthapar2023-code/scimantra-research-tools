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
<div class="hero"><h1>🔬 SciMantra Research Tools</h1><p>Calculate • Analyze • Visualize • Understand — practical tools for science, laboratory work and research.</p></div>
""", unsafe_allow_html=True)

st.sidebar.title("SCIMantra")
st.sidebar.caption("Science • Research • Learning")
section = st.sidebar.radio("Choose a tool", [
    "🏠 Dashboard", "🧪 Laboratory Calculators", "📊 Statistics", "🌱 Environmental Biotechnology",
    "📈 Data Analyzer", "📊 Advanced Experimental Data Analysis", "🔬 Research Tools", "🌍 TEA & LCA"
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

if section == "📊 Advanced Experimental Data Analysis":
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
        mass=st.number_input("Mass of solute (g)",min_value=0.,value=1.); mw=st.number_input("Molecular weight (g/mol)",min_value=1e-6,value=58.44); vol=st.number_input("Final volume (L)",min_value=1e-6,value=1.); st.metric("Molarity",f"{mass/mw/vol:.6g} mol/L")
    elif tool.startswith("Dilution"):
        c1=st.number_input("C₁",min_value=0.,value=100.); c2=st.number_input("C₂",min_value=1e-6,value=10.); v2=st.number_input("V₂",min_value=1e-6,value=100.); v1=c2*v2/c1 if c1 else 0; st.metric("Stock volume V₁",f"{v1:.4g}"); st.metric("Diluent volume",f"{v2-v1:.4g}")
    elif tool=="% Solution":
        st.selectbox("Type",["w/v","w/w","v/v"]); amount=st.number_input("Solute amount",min_value=0.,value=5.); total=st.number_input("Total amount/volume",min_value=1e-6,value=100.); st.metric("Percentage",f"{amount/total*100:.4g}%")
    elif tool=="Normality":
        m=st.number_input("Molarity (mol/L)",min_value=0.,value=1.); n=st.number_input("n-factor",min_value=1e-6,value=1.); st.metric("Normality",f"{m*n:.6g} N")
    elif tool=="CFU/mL":
        colonies=st.number_input("Colonies",min_value=0.,value=125.); dilution=st.number_input("Reciprocal dilution",min_value=1.,value=100000.); plated=st.number_input("Volume plated (mL)",min_value=1e-6,value=.1); st.metric("CFU/mL",f"{colonies*dilution/plated:.6g}")
    elif tool=="Biomass concentration":
        dry=st.number_input("Dry biomass (g)",min_value=0.,value=1.); v=st.number_input("Culture volume (L)",min_value=1e-6,value=1.); st.metric("Biomass",f"{dry/v:.6g} g/L")
    elif tool=="Growth rate":
        x1=st.number_input("Measurement 1",value=.1); x2=st.number_input("Measurement 2",value=.8); t1=st.number_input("Time 1",value=0.); t2=st.number_input("Time 2",value=10.); st.metric("Growth rate",f"{(x2-x1)/(t2-t1):.6g}" if t2!=t1 else "N/A")
    elif tool=="Specific growth rate":
        x1=st.number_input("X₁",min_value=1e-6,value=.1); x2=st.number_input("X₂",min_value=1e-6,value=.8); dt=st.number_input("Δt",min_value=1e-6,value=10.); st.metric("μ",f"{math.log(x2/x1)/dt:.6g} time⁻¹")
    elif tool=="BOD":
        initial=st.number_input("Initial DO (mg/L)",value=8.); final=st.number_input("Final DO (mg/L)",value=3.); sample=st.number_input("Sample volume (mL)",min_value=1e-6,value=15.); bottle=st.number_input("Bottle volume (mL)",min_value=1e-6,value=300.); st.metric("Approx. BOD₅",f"{(initial-final)*bottle/sample:.6g} mg/L")
    else:
        a=st.number_input("Blank titration A (mL)",value=20.); b=st.number_input("Sample titration B (mL)",value=12.); normality=st.number_input("Titrant normality",min_value=1e-6,value=.1); volume=st.number_input("Sample volume (mL)",min_value=1e-6,value=10.); st.metric("COD",f"{(a-b)*normality*8000/volume:.6g} mg/L")

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
        try: xx=np.array([float(v) for v in x.split(",") if v.strip()]); yy=np.array([float(v) for v in y.split(",") if v.strip()]); r=stats.linregress(xx,yy); c=st.columns(4); c[0].metric("Slope",f"{r.slope:.6g}"); c[1].metric("Intercept",f"{r.intercept:.6g}"); c[2].metric("R²",f"{r.rvalue**2:.6g}"); c[3].metric("p-value",f"{r.pvalue:.6g}"); order=np.argsort(xx); st.plotly_chart(go.Figure([go.Scatter(x=xx,y=yy,mode="markers"),go.Scatter(x=xx[order],y=r.intercept+r.slope*xx[order],mode="lines")]),use_container_width=True)
        except Exception: st.warning("Enter equal-length arrays.")

elif section == "🌱 Environmental Biotechnology":
    tool=st.selectbox("Environmental tool",["Removal efficiency","Loading rate","EBRT","H₂S removal"])
    if tool=="Removal efficiency":
        cin=st.number_input("Influent concentration",value=100.); cout=st.number_input("Effluent concentration",value=20.); st.metric("Removal efficiency",f"{(cin-cout)/cin*100:.4g}%" if cin else "N/A")
    elif tool=="Loading rate":
        concentration=st.number_input("Concentration",value=100.,min_value=0.); flow=st.number_input("Flow rate",value=1.,min_value=1e-9); st.metric("Loading",f"{concentration*flow:.6g} mass/time")
    elif tool=="EBRT":
        volume=st.number_input("Reactor volume",value=1.,min_value=0.); flow=st.number_input("Gas flow",value=1.,min_value=1e-9); st.metric("EBRT",f"{volume/flow:.6g} time")
    else:
        cin=st.number_input("H₂S inlet",value=100.); cout=st.number_input("H₂S outlet",value=20.); st.metric("H₂S removal",f"{(cin-cout)/cin*100:.4g}%" if cin else "N/A")

elif section == "📈 Data Analyzer":
    st.subheader("Data Analyzer")
    uploaded=st.file_uploader("Upload Excel/CSV",type=["xlsx","csv"])
    if uploaded:
        df=pd.read_csv(uploaded) if uploaded.name.lower().endswith(".csv") else pd.read_excel(uploaded)
        st.dataframe(df,use_container_width=True)
        numeric=df.select_dtypes(include=np.number).columns.tolist()
        if numeric:
            col=st.selectbox("Variable",numeric); st.dataframe(df[col].describe().to_frame().T,use_container_width=True); st.plotly_chart(px.histogram(df,x=col,title=f"Distribution: {col}"),use_container_width=True)
    else: st.info("Upload an Excel or CSV file to begin.")

elif section == "🔬 Research Tools":
    st.subheader("Research Utilities")
    tool=st.selectbox("Tool",["Standard curve","Experimental design checklist","Manuscript checklist"])
    if tool=="Standard curve":
        x=st.text_input("Concentrations", "1,2,3,4,5"); y=st.text_input("Responses", "2,4,6,8,10")
        try:
            xx=np.array([float(v) for v in x.split(",")]); yy=np.array([float(v) for v in y.split(",")]); r=stats.linregress(xx,yy); st.metric("R²",f"{r.rvalue**2:.6g}"); st.code(f"y = {r.slope:.6g}x + {r.intercept:.6g}")
        except Exception: st.warning("Enter matching numeric values.")
    elif tool=="Experimental design checklist":
        for item in ["Research question defined","Controls defined","Independent replicates defined","Technical replicates distinguished","Primary endpoint defined","Sample size justified","Randomization/blinding considered","Statistical test pre-specified"]: st.checkbox(item)
    else:
        for item in ["Title and abstract","Methods reproducibility","Replicate definition","Statistical methods","Figures and tables","Limitations","References","Data availability"]: st.checkbox(item)

elif section == "🌍 TEA & LCA":
    st.header("🌍 Sustainability & Process Evaluation")
    st.caption("Techno-Economic Analysis (TEA) and Life Cycle Assessment (LCA) — transparent research decision-support tools")
    mode=st.radio("Analysis",["TEA","LCA"],horizontal=True)
    if mode=="TEA":
        st.subheader("1. Project & production assumptions")
        c1,c2,c3,c4=st.columns(4)
        currency=c1.selectbox("Currency",["₹","$","€","£"]); life=c2.number_input("Project life (years)",1,100,10); price=c3.number_input("Selling value / avoided treatment cost",0.,1000000.,100.); tax=c4.number_input("Tax rate (%)",0.,100.,25.)/100
        c1,c2,c3,c4=st.columns(4); annual_output=c1.number_input("Annual output",1e-9,1e12,1000.); capacity=c2.number_input("Capacity factor (%)",0.,100.,90.)/100; discount=c3.number_input("Discount rate (%)",0.,100.,10.)/100; salvage_pct=c4.number_input("Salvage (%)",0.,100.,5.)/100
        st.subheader("2. Capital expenditure (CAPEX)")
        c1,c2,c3,c4=st.columns(4); equipment=c1.number_input("Equipment",0.,1e12,500000.); engineering=c2.number_input("Engineering",0.,1e12,75000.); other_capex=c3.number_input("Other CAPEX",0.,1e12,0.); installation=c4.number_input("Installation / civil",0.,1e12,150000.)
        c1,c2=st.columns(2); contingency=c1.number_input("Contingency (%)",0.,100.,10.)/100; working_capital=c2.number_input("Initial working capital",0.,1e12,50000.)
        st.subheader("3. Annual operating expenditure (OPEX)")
        c1,c2,c3,c4=st.columns(4); fixed_opex=c1.number_input("Fixed OPEX",0.,1e12,100000.); utilities=c2.number_input("Utilities",0.,1e12,80000.); variable_cost=c3.number_input("Variable cost / output unit",0.,1e9,20.); labor=c4.number_input("Labor",0.,1e12,120000.)
        direct=equipment+engineering+other_capex+installation; total_capex=direct*(1+contingency); initial=total_capex+working_capital; effective_output=annual_output*capacity; maintenance=total_capex*.04; fixed_cash=fixed_opex+utilities+labor+maintenance; variable_opex=variable_cost*effective_output; annual_opex=fixed_cash+variable_opex; revenue=price*effective_output; ebitda=revenue-annual_opex; depreciation=total_capex/life; ebit=ebitda-depreciation; tax_cash=max(0,ebit*tax); fcf=ebitda-tax_cash; salvage=total_capex*salvage_pct; cf=[-initial]+[fcf for _ in range(life)]; cf[-1]+=salvage+working_capital
        npv=npv_of(cf,discount); roots=irr_roots(cf); roi=(sum(cf[1:])-initial)/initial*100; pv_future=sum(cf[i]/((1+discount)**i) for i in range(1,len(cf))); pi=pv_future/initial
        cash_be=variable_cost+fixed_cash/effective_output if effective_output else np.nan; accounting_be=variable_cost+(fixed_cash+depreciation)/effective_output if effective_output else np.nan; break_volume=fixed_cash/(price-variable_cost) if price>variable_cost else np.nan
        try: min_price=price-brentq(lambda p: npv_of([-initial]+[(p*effective_output-annual_opex-max(0,(p*effective_output-annual_opex-depreciation)*tax)) for _ in range(life-1)]+[(p*effective_output-annual_opex-max(0,(p*effective_output-annual_opex-depreciation)*tax))+salvage+working_capital],discount),-1e6,1e6) if False else brentq(lambda p: npv_of([-initial]+[(p*effective_output-annual_opex-max(0,(p*effective_output-annual_opex-depreciation)*tax)) for _ in range(life-1)]+[(p*effective_output-annual_opex-max(0,(p*effective_output-annual_opex-depreciation)*tax))+salvage+working_capital],discount),0,1e6)
        except Exception: min_price=np.nan
        st.subheader("Key TEA results")
        vals=[("Total CAPEX",total_capex),("Initial investment",initial),("Annual revenue",revenue),("Annual OPEX",annual_opex),("Annual FCF",fcf),("NPV",npv),("IRR",(roots[0]*100 if roots else np.nan)),("Simple payback",payback(cf)),("Discounted payback",payback(cf,True,discount)),("ROI (project life)",roi),("Profitability index",pi)]
        for i,(lab,val) in enumerate(vals):
            with st.container():
                if i%4==0: cols=st.columns(4)
                cols[i%4].metric(lab, "N/A" if (isinstance(val,float) and np.isnan(val)) else (f"{currency}{val:,.2f}" if lab not in ["IRR","ROI (project life)","Simple payback","Discounted payback","Profitability index"] else (f"{val:.2f}%" if lab in ["IRR","ROI (project life)"] else (f"{val:.2f}" if lab=="Profitability index" else ("Not reached" if np.isnan(val) else f"{val:.2f} years")))))
        st.subheader("Break-even & investment indicators")
        b=st.columns(4); b[0].metric("Cash break-even value / unit",f"{currency}{cash_be:,.2f}"); b[1].metric("Accounting break-even value / unit",f"{currency}{accounting_be:,.2f}"); b[2].metric("Break-even annual volume",f"{break_volume:,.2f}"); b[3].metric("NPV-zero minimum selling value",f"{currency}{min_price:,.2f}" if np.isfinite(min_price) else "N/A")
        st.caption("Cash break-even excludes depreciation; accounting break-even includes depreciation. Minimum selling value is the unit value required for NPV ≈ 0 at the selected discount rate.")
        cfdf=pd.DataFrame({"Year":range(len(cf)),"Cashflow":cf}); st.plotly_chart(px.bar(cfdf,x="Year",y="Cashflow",title="Cash-flow profile"),use_container_width=True)
        st.subheader("Scenario analysis")
        scen=[]
        for name,pm,vm in [("Conservative",.8,1.2),("Base",1.,1.),("Optimistic",1.2,.8)]:
            r=price*pm*effective_output-(fixed_cash+variable_cost*vm*effective_output); scen.append({"Scenario":name,"Annual FCF":r,"Selling value multiplier":pm,"Variable cost multiplier":vm})
        st.dataframe(pd.DataFrame(scen),use_container_width=True)
        sell_mult=np.linspace(.8,1.2,9); cost_mult=np.linspace(.8,1.2,9); z=[]
        for cm in cost_mult:
            row=[]
            for sm in sell_mult:
                f=price*sm*effective_output-(fixed_cash+variable_cost*cm*effective_output); cfs=[-initial]+[f for _ in range(life)]; cfs[-1]+=salvage+working_capital; row.append(npv_of(cfs,discount))
            z.append(row)
        st.plotly_chart(px.imshow(z,x=sell_mult,y=cost_mult,labels={"x":"Selling value multiplier","y":"Variable-cost multiplier","color":"NPV"},title="NPV sensitivity: selling value vs variable cost"),use_container_width=True)
        st.markdown("**Research interpretation:** NPV < 0 means the default assumptions do not recover the initial investment at the selected discount rate. IRR is reported only when a valid positive-rate root exists.")
    else:
        st.subheader("1. Goal, scope & functional unit")
        c1,c2=st.columns(2); goal=c1.text_area("Goal","Compare the environmental burden of two process scenarios."); assessment=c2.text_input("Assessment name","SciMantra screening LCA"); fu=c1.text_input("Functional unit (one service/product basis)","1 kg product"); ref_unit=c1.text_input("Reference flow / output unit","kg product"); boundary=c1.selectbox("System boundary",["Gate-to-gate","Cradle-to-gate","Cradle-to-grave"]); ref_qty=c2.number_input("Reference flow quantity",0.000001,1e12,1000.); year=c2.number_input("Data/reference year",1900,2100,2026); geography=c2.text_input("Geography / context","Specify country, region or site"); technology=c2.text_input("Technology / process description","Specify process configuration")
        st.caption(f"Normalization basis: {ref_qty:g} {ref_unit}. Report results per the functional unit {fu}; keep the inventory reference flow explicit and consistent.")
        st.subheader("2. Life-cycle inventory")
        default=pd.DataFrame([{"Flow":"Electricity","Quantity":100,"Unit":"kWh","Emission_factor":.7,"EF_unit":"kg CO2e/unit","Stage":"Operation","Category":"Energy","Source":"Example assumption","Geography":"Specify","Data_year":year,"Uncertainty_%":0},{"Flow":"Water","Quantity":2,"Unit":"m³","Emission_factor":.3,"EF_unit":"kg CO2e/unit","Stage":"Operation","Category":"Water","Source":"Example assumption","Geography":"Specify","Data_year":year,"Uncertainty_%":0},{"Flow":"Chemical","Quantity":5,"Unit":"kg","Emission_factor":2.,"EF_unit":"kg CO2e/unit","Stage":"Upstream","Category":"Material","Source":"Example assumption","Geography":"Specify","Data_year":year,"Uncertainty_%":0},{"Flow":"Transport","Quantity":50,"Unit":"tkm","Emission_factor":.1,"EF_unit":"kg CO2e/unit","Stage":"Transport","Category":"Transport","Source":"Example assumption","Geography":"Specify","Data_year":year,"Uncertainty_%":0}])
        inv=st.data_editor(default,use_container_width=True,num_rows="dynamic")
        q=pd.to_numeric(inv["Quantity"],errors="coerce").fillna(0); ef=pd.to_numeric(inv["Emission_factor"],errors="coerce").fillna(0); inv["CO2e_kg"]=q*ef; total=float(inv["CO2e_kg"].sum()); intensity=total/ref_qty if ref_qty else np.nan
        unc=pd.to_numeric(inv.get("Uncertainty_%",pd.Series([0]*len(inv))),errors="coerce").fillna(0)/100; sigma=float(np.sqrt(np.sum((inv["CO2e_kg"]*unc)**2))); lo=max(0,total-1.96*sigma); hi=total+1.96*sigma
        st.subheader("3. Results"); c=st.columns(3); c[0].metric("Total inventory GHG burden",f"{total:.3f} kg CO₂e"); c[1].metric("GHG intensity",f"{intensity:.6f} kg CO₂e / reference-output unit"); c[2].metric("Approx. uncertainty range",f"{lo:.3f}–{hi:.3f} kg CO₂e")
        st.caption(f"Functional unit: {fu}. Reference flow: {ref_qty:g} {ref_unit}. The uncertainty range is an approximate independent-error screen based only on user-entered row uncertainties; it is not a Monte Carlo confidence interval.")
        stage=inv.groupby("Stage",dropna=False)["CO2e_kg"].sum().reset_index(); cat=inv.groupby("Category",dropna=False)["CO2e_kg"].sum().reset_index(); c1,c2=st.columns(2); c1.plotly_chart(px.bar(stage,x="Stage",y="CO2e_kg",title="Contribution by life-cycle stage"),use_container_width=True); c2.plotly_chart(px.bar(cat,x="Category",y="CO2e_kg",title="Contribution by inventory category"),use_container_width=True)
        st.subheader("4. Scenario comparison")
        scen=st.data_editor(pd.DataFrame([{"Scenario":"Baseline","Total_CO2e_kg":total},{"Scenario":"Alternative","Total_CO2e_kg":total*.8}]),use_container_width=True,num_rows="dynamic"); scen["kg_CO2e_per_FU"]=scen["Total_CO2e_kg"]/ref_qty; base=float(scen.iloc[0]["Total_CO2e_kg"]) if len(scen) else np.nan; scen["Reduction_vs_baseline_%"]=(base-scen["Total_CO2e_kg"])/base*100 if base else np.nan; st.dataframe(scen,use_container_width=True); st.plotly_chart(px.bar(scen,x="Scenario",y="kg_CO2e_per_FU",title="Scenario GHG intensity"),use_container_width=True)
        st.subheader("5. Sensitivity analysis"); valid=inv["Flow"].astype(str).tolist(); flow=st.selectbox("Flow to vary",valid); lo_pct,hi_pct=st.slider("Flow quantity range (%)",-80,200,(-50,50)); base_q=float(q[inv["Flow"].astype(str)==flow].sum()); multipliers=np.linspace(1+lo_pct/100,1+hi_pct/100,11); other=total-base_q*float(ef[inv["Flow"].astype(str)==flow].sum())/max(1,int((inv["Flow"].astype(str)==flow).sum())) if base_q else total; row=inv[inv["Flow"].astype(str)==flow].iloc[0]; contribution=float(row["CO2e_kg"]); vals=(total-contribution)+contribution*multipliers; sens=pd.DataFrame({"Quantity multiplier":multipliers,"kg CO2e / FU":vals/ref_qty}); st.plotly_chart(px.line(sens,x="Quantity multiplier",y="kg CO2e / FU",markers=True,title=f"LCA sensitivity: {flow}"),use_container_width=True)
        share=contribution/total*100 if total else 0; st.info(f"Sensitivity driver: **{flow}** contributes approximately **{share:.1f}%** of baseline GHG burden. Focus data-quality improvement and scenario testing on high-contribution flows.")
        with st.expander("6. Data quality & methodology record"):
            st.write({"Goal":goal,"Assessment":assessment,"Functional unit":fu,"Reference flow":f"{ref_qty:g} {ref_unit}","System boundary":boundary,"Geography":geography,"Technology":technology,"Reference year":year})
        st.caption("Screening-level LCA aid. Emission factors should be sourced from appropriate databases/literature and matched to geography, technology, system boundary and functional unit before publication.")
