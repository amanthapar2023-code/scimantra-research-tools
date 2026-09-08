import math
import numpy as np
import pandas as pd
import streamlit as st
from scipy import stats
from scipy.optimize import brentq
import plotly.express as px
import plotly.graph_objects as go
from src.scimantra.laboratory import molarity_from_mass, dilution_stock_volume, solution_percentage, normality_from_molarity, cfu_per_ml, biomass_concentration, growth_rate, specific_growth_rate, bod_approx, cod_from_titration
from src.scimantra.environmental import removal_efficiency, loading_rate, ebrt, h2s_removal

st.set_page_config(page_title="SciMantra Research Platform", page_icon="🔬", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
.block-container{max-width:1450px;padding-top:1.2rem;padding-bottom:3rem}.hero{padding:2rem 2.2rem;border-radius:22px;background:linear-gradient(135deg,#e9f4ff 0%,#f8fbff 55%,#eefaf5 100%);border:1px solid #d8e8f5;margin-bottom:1.3rem;box-shadow:0 6px 24px rgba(20,55,80,.06)}
.hero h1{margin:0;color:#0b2033;font-size:2.55rem;font-weight:750}.hero p{margin:.5rem 0 0;color:#486176;font-size:1.08rem}.eyebrow{font-size:.78rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:#2574a8;margin-bottom:.35rem}.section-title{font-size:1.45rem;font-weight:700;color:#102b40;margin:1.1rem 0 .7rem}.tool-card{border:1px solid #dfe8ee;border-radius:16px;padding:1.05rem 1.1rem;background:#fff;min-height:132px;margin-bottom:.9rem;box-shadow:0 3px 12px rgba(20,55,80,.045)}
.tool-card h3{margin:0 0 .35rem;color:#17344a;font-size:1.12rem}.tool-card p{margin:0;color:#536b7b;line-height:1.5}.pro-card{background:linear-gradient(135deg,#fffdf5,#fff);border-color:#ead9a5}
.flow-grid{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:12px}.flow{border:1px solid #dfe8ee;border-radius:14px;padding:1rem;text-align:center;background:#fff;min-height:92px;display:flex;flex-direction:column;justify-content:center;box-sizing:border-box}.flow strong{display:block;color:#18364b}.flow span{font-size:.86rem;color:#637889}footer{visibility:hidden}
@media(max-width:1100px){.flow-grid{grid-template-columns:repeat(3,minmax(0,1fr))}}@media(max-width:700px){.block-container{padding-left:.8rem;padding-right:.8rem}.hero{padding:1.35rem}.hero h1{font-size:2rem}.hero p{font-size:.98rem}.flow-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}.flow{min-height:78px;padding:.7rem}.section-title{font-size:1.25rem}}
</style>
""",unsafe_allow_html=True)

st.sidebar.markdown("# 🔬 SciMantra")
st.sidebar.caption("Research • Analysis • Discovery")
st.sidebar.divider()
if "scimantra_page" not in st.session_state: st.session_state.scimantra_page="🏠 Dashboard"
def nav(label,key):
    if st.sidebar.button(label,key=key,width="stretch"): st.session_state.scimantra_page=label
st.sidebar.markdown("**🏠 WORKSPACE**"); nav("🏠 Dashboard","nav_dashboard")
st.sidebar.markdown("**🧪 CORE RESEARCH**")
for label,key in [("🧪 Laboratory Calculators","nav_lab"),("📊 Statistics","nav_stats"),("🌱 Environmental Biotechnology","nav_env"),("📈 Data Analyzer","nav_data"),("📊 Advanced Analysis","nav_advanced"),("🔬 Research Tools","nav_research"),("🌍 TEA & LCA","nav_tea")]: nav(label,key)
st.sidebar.markdown("**⭐ PRO RESEARCH SUITE**")
for label,key in [("SciMantra Pro Workspace","nav_pro_workspace"),("AI Research Assistant","nav_ai"),("Statistical Copilot","nav_copilot"),("Publication Figure Generator","nav_figures"),("Automated Research Report","nav_report"),("Experimental Design Power Analysis","nav_power")]: nav(label,key)
st.sidebar.markdown("**☁️ ACCOUNT & PROJECTS**")
for label,key in [("Research Project Manager","nav_projects"),("Accounts Project Hub","nav_accounts"),("Subscriptions and Pro","nav_subscriptions"),("Login and Cloud Account","nav_login"),("Cloud Project Workspace","nav_cloud"),("Account Dashboard","nav_dashboard_account"),("Admin Control Center","nav_admin")]: nav(label,key)
section=st.session_state.scimantra_page

st.markdown('<div class="hero"><div class="eyebrow">Integrated research platform</div><h1>🔬 SciMantra</h1><p><b>Research. Analyze. Visualize. Publish.</b><br>Practical scientific tools for laboratory calculations, experimental data, environmental biotechnology and research reporting.</p></div>',unsafe_allow_html=True)

def download_df(df,filename="scimantra_results.csv"): st.download_button("⬇️ Download CSV",df.to_csv(index=False).encode("utf-8"),filename,"text/csv")
def irr_roots(cashflows,max_rate=1000.0):
    cf=np.asarray(cashflows,dtype=float)
    if len(cf)<2 or not(np.any(cf>0) and np.any(cf<0)): return []
    def f(r): return sum(v/((1+r)**i) for i,v in enumerate(cf))
    grid=np.unique(np.concatenate(([-.9999,-.99,-.9,-.5,-.1,0.0],np.geomspace(1e-8,max_rate,300)))); vals=[f(float(r)) for r in grid]; roots=[]
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
def npv_of(cf,rate): return sum(v/((1+rate)**i) for i,v in enumerate(cf))
def payback(cf,discounted=False,rate=0.0):
    cumulative=0.0
    for i,v in enumerate(cf):
        pv=v/((1+rate)**i) if discounted else v; prev=cumulative; cumulative+=pv
        if cumulative>=0 and i>0: return float(i) if pv==0 else (i-1)+max(0,min(1,-prev/pv))
    return np.nan

if section=="🏠 Dashboard":
    st.markdown('<div class="section-title">Everything you need for the research workflow</div>',unsafe_allow_html=True)
    cols=st.columns(3)
    cards=[("🧪 Laboratory","Molarity, dilution, CFU/mL, BOD, COD, biomass and growth calculations."),("📊 Statistics","Mean, SD, SEM, CV, t-test, ANOVA, correlation and regression."),("🌱 Environment","Removal efficiency, loading, EBRT and H₂S analysis."),("📈 Data Analyzer","Upload Excel/CSV files, summarize replicates and create interactive graphs."),("📊 Advanced Analysis","Replicate-aware statistics, regression, time-series and research-grade visualization."),("🔬 Research","Standard curves, experimental design and manuscript checklists."),("🌍 TEA & LCA","Screen process economics, NPV, IRR, life-cycle inventory and CO₂e intensity."),("⭐ Pro Research Suite","AI assistance, statistical copilot, publication figures, automated reports and power analysis.")]
    for i,(title,desc) in enumerate(cards):
        with cols[i%3]: st.markdown(f'<div class="tool-card {"pro-card" if "Pro" in title else ""}"><h3>{title}</h3><p>{desc}</p></div>',unsafe_allow_html=True)
    st.markdown('<div class="section-title">🔄 Research workflow</div>',unsafe_allow_html=True)
    flow_titles=[("Upload","Dataset"),("Analyze","Quality & trends"),("Statistics","Evidence"),("Visualize","Figures"),("Report","Manuscript"),("Publish","Research-ready output")]
    st.markdown('<div class="flow-grid">'+''.join(f'<div class="flow"><strong>{a}</strong><span>{b}</span></div>' for a,b in flow_titles)+'</div>',unsafe_allow_html=True)
    st.markdown("<br>",unsafe_allow_html=True)
    c1,c2=st.columns([2,1]); c1.success("**Start with your data:** use Data Analyzer for quick exploration or Advanced Analysis for replicate-aware research workflows."); c2.info("⭐ **Pro:** unlock the full analysis → figure → report workflow.")

elif section=="🧪 Laboratory Calculators":
    from src.scimantra.lab_ui import render as render_lab_ui; render_lab_ui()

elif section=="📊 Statistics":
    tool=st.selectbox("Statistical tool",["Descriptive statistics","t-Test","One-way ANOVA","Correlation","Linear regression"])
    if tool=="Descriptive statistics":
        vals=st.text_area("Values separated by commas","1,2,3,4,5,6")
        try:
            x=np.array([float(v.strip()) for v in vals.split(",") if v.strip()]); c=st.columns(4); c[0].metric("Mean",f"{x.mean():.5g}"); c[1].metric("SD",f"{x.std(ddof=1):.5g}" if len(x)>1 else "NA"); c[2].metric("SEM",f"{stats.sem(x):.5g}" if len(x)>1 else "NA"); c[3].metric("CV %",f"{x.std(ddof=1)/x.mean()*100:.5g}" if len(x)>1 and x.mean()!=0 else "NA")
        except Exception: st.error("Please enter numeric values.")
    elif tool=="t-Test":
        a=st.text_area("Group A","1,2,3,4,5"); b=st.text_area("Group B","2,3,4,5,6")
        try: x=[float(v) for v in a.split(",") if v.strip()]; y=[float(v) for v in b.split(",") if v.strip()]; r=stats.ttest_ind(x,y,equal_var=False); st.metric("t statistic",f"{r.statistic:.6g}"); st.metric("p-value",f"{r.pvalue:.6g}")
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
        try:
            xx=np.array([float(v) for v in x.split(",") if v.strip()]); yy=np.array([float(v) for v in y.split(",") if v.strip()]); r=stats.linregress(xx,yy); c=st.columns(4); c[0].metric("Slope",f"{r.slope:.6g}"); c[1].metric("Intercept",f"{r.intercept:.6g}"); c[2].metric("R²",f"{r.rvalue**2:.6g}"); c[3].metric("p-value",f"{r.pvalue:.6g}"); order=np.argsort(xx); st.plotly_chart(go.Figure([go.Scatter(x=xx,y=yy,mode="markers"),go.Scatter(x=xx[order],y=r.intercept+r.slope*xx[order],mode="lines")]),width="stretch")
        except Exception: st.warning("Enter equal-length arrays.")

elif section=="🌱 Environmental Biotechnology":
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

elif section=="📈 Data Analyzer":
    from src.scimantra.data_ui import render as render_data_ui; render_data_ui()

elif section=="🔬 Research Tools":
    st.subheader("Research Utilities"); tool=st.selectbox("Tool",["Standard curve","Experimental design checklist","Manuscript checklist"])
    if tool=="Standard curve":
        x=st.text_input("Concentrations","1,2,3,4,5"); y=st.text_input("Response","2,4,5,8,10")
        try: xx=np.array([float(v) for v in x.split(",") if v.strip()]); yy=np.array([float(v) for v in y.split(",") if v.strip()]); r=stats.linregress(xx,yy); st.metric("R²",f"{r.rvalue**2:.6g}"); order=np.argsort(xx); st.plotly_chart(go.Figure([go.Scatter(x=xx,y=yy,mode="markers"),go.Scatter(x=xx[order],y=r.intercept+r.slope*xx[order],mode="lines")]),width="stretch")
        except Exception: st.warning("Enter equal-length numeric arrays.")
    elif tool=="Experimental design checklist":
        for item in ["Define hypothesis","Identify independent/dependent variables","Choose controls","Set biological/technical replicates","Define sample size","Predefine statistical analysis","Document units and conditions"]: st.checkbox(item)
    else:
        for item in ["Title and abstract","Methods reproducibility","Statistical reporting","Figures and tables","References","Limitations","Data/code availability"]: st.checkbox(item)

elif section=="🌍 TEA & LCA":
    st.subheader("Techno-Economic Analysis & Life-Cycle Assessment"); st.caption("Screening-level calculations for research planning; document assumptions and verify with project-specific data."); st.write("Use the existing TEA & LCA tools below to model NPV, IRR, payback, inventory and CO₂e intensity.")

elif section=="📊 Advanced Analysis":
    import runpy; runpy.run_path("pages/7_Advanced_Experimental_Data_Analysis.py"); st.stop()

elif section in {"SciMantra Pro Workspace","AI Research Assistant","Statistical Copilot","Publication Figure Generator","Automated Research Report","Experimental Design Power Analysis","Research Project Manager","Accounts Project Hub","Subscriptions and Pro","Login and Cloud Account","Cloud Project Workspace","Account Dashboard","Admin Control Center"}:
    import runpy
    page_map={"SciMantra Pro Workspace":"pages/8_SciMantra_Pro_Workspace.py","AI Research Assistant":"pages/9_AI_Research_Assistant.py","Statistical Copilot":"pages/10_Statistical_Copilot.py","Publication Figure Generator":"pages/11_Publication_Figure_Generator.py","Automated Research Report":"pages/12_Automated_Research_Report.py","Experimental Design Power Analysis":"pages/13_Experimental_Design_Power_Analysis.py","Research Project Manager":"pages/14_Research_Project_Manager.py","Accounts Project Hub":"pages/15_Accounts_Project_Hub.py","Subscriptions and Pro":"pages/16_Subscriptions_and_Pro.py","Login and Cloud Account":"pages/17_Login_and_Cloud_Account.py","Cloud Project Workspace":"pages/18_Cloud_Project_Workspace.py","Account Dashboard":"pages/19_Account_Dashboard.py","Admin Control Center":"pages/20_Admin_Control_Center.py"}
    runpy.run_path(page_map[section])
