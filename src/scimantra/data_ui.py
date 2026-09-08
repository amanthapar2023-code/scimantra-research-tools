from __future__ import annotations

import io
import re
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from scipy import stats
from src.scimantra.research_session import store_dataframe


def _excel_sheets(uploaded):
    uploaded.seek(0)
    book = pd.ExcelFile(uploaded)
    return book, book.sheet_names


def _load(uploaded, sheet_name=None):
    uploaded.seek(0)
    if uploaded.name.lower().endswith(".csv"):
        return pd.read_csv(uploaded)
    return pd.read_excel(uploaded, sheet_name=sheet_name)


def _download(df: pd.DataFrame):
    st.download_button("⬇️ Download selected data", df.to_csv(index=False).encode("utf-8"), "scimantra_data.csv", "text/csv", width="stretch")


def _summary(df: pd.DataFrame, selected: list[str]) -> pd.DataFrame:
    rows=[]
    for col in selected:
        x=pd.to_numeric(df[col],errors="coerce").dropna().to_numpy(dtype=float); n=len(x)
        mean=float(np.mean(x)) if n else np.nan; sd=float(np.std(x,ddof=1)) if n>1 else np.nan
        sem=sd/np.sqrt(n) if n>1 else np.nan; cv=(sd/mean*100) if n>1 and mean!=0 else np.nan
        rows.append({"Variable":col,"N":n,"Mean":mean,"SD":sd,"SEM":sem,"CV %":cv,"Median":float(np.median(x)) if n else np.nan,"Min":float(np.min(x)) if n else np.nan,"Max":float(np.max(x)) if n else np.nan})
    return pd.DataFrame(rows)


def _measurement_columns(df: pd.DataFrame) -> list[str]:
    numeric=[]
    for col in df.columns:
        converted=pd.to_numeric(df[col],errors="coerce"); original=int(df[col].notna().sum()); valid=int(converted.notna().sum())
        if original and valid/original>=0.8: numeric.append(col)
    return numeric


















































def _relationship_columns(df: pd.DataFrame, numeric: list[str]) -> list[str]:
    """Return useful numeric variables for correlation, excluding worksheet artifacts and repeated calculations."""
    candidates = []
    for col in numeric:
        name = str(col).strip().lower()
        if not name or name.startswith("unnamed"):
            continue
        x = pd.to_numeric(df[col], errors="coerce")
        if x.notna().sum() < 3 or x.nunique(dropna=True) < 2:
            continue
        candidates.append((col, x))

    selected = []
    seen_bases = set()
    for col, x in candidates:
        base = re.sub(r"\.\d+$", "", str(col)).strip().lower()
        if base in seen_bases:
            continue
        duplicate = False
        for _, prev in selected:
            paired = pd.concat([x.reset_index(drop=True), prev.reset_index(drop=True)], axis=1).dropna()
            if len(paired) >= 3 and np.allclose(
                paired.iloc[:, 0].to_numpy(dtype=float),
                paired.iloc[:, 1].to_numpy(dtype=float),
                rtol=1e-10,
                atol=1e-12,
            ):
                duplicate = True
                break
        if not duplicate:
            selected.append((col, x))
            seen_bases.add(base)
    return [col for col, _ in selected]

def _sheet_score(df: pd.DataFrame) -> tuple[int,int,int]:
    cols=_measurement_columns(df); cells=sum(int(pd.to_numeric(df[c],errors="coerce").notna().sum()) for c in cols); rows=int(df.notna().any(axis=1).sum())
    return len(cols),cells,rows


def _find_columns(df: pd.DataFrame, keywords: list[str]) -> list[str]:
    return [c for c in df.columns if any(k in str(c).lower().replace("₂","2") for k in keywords)]


def _num(df: pd.DataFrame, col: str) -> pd.Series:
    return pd.to_numeric(df[col], errors="coerce")


def _environmental_h2s(df: pd.DataFrame, numeric: list[str]) -> None:
    """Environmental-biotechnology analysis layer for H2S/reactor datasets."""
    st.markdown("### 🌱 H₂S & reactor research analysis")
    st.caption("SciMantra detects likely H₂S, time, pH, flow, EBRT, loading and treatment columns. Calculations are screening-level and preserve the original observations.")

    h2s_cols=_find_columns(df,["h2s","h₂s","hydrogen sulfide","sulfide","sulphide"])
    time_cols=_find_columns(df,["time","hour","hr","day","minute","min","ebrt"])
    ph_cols=_find_columns(df,["ph"])
    flow_cols=_find_columns(df,["flow","gas flow","air flow"])
    volume_cols=_find_columns(df,["reactor volume","volume","bed volume"])
    treatment_cols=[c for c in df.columns if c not in numeric and c not in h2s_cols and c not in time_cols]

    if not h2s_cols:
        st.warning("No H₂S/sulfide-like column was detected automatically. Rename a concentration column to include H₂S, sulfide, or sulphide, or continue with the general analysis tabs.")
        return

    c1,c2,c3,c4=st.columns(4)
    c1.metric("H₂S candidates",len(h2s_cols)); c2.metric("Time candidates",len(time_cols)); c3.metric("pH candidates",len(ph_cols)); c4.metric("Flow candidates",len(flow_cols))

    mode=st.selectbox("Environmental analysis",["H₂S time-course","Influent → effluent removal","Treatment/group comparison","H₂S vs pH / operating variable","Reactor loading & EBRT"])

    if mode=="H₂S time-course":
        y=st.selectbox("H₂S response",h2s_cols)
        x_options=time_cols or numeric
        x=st.selectbox("Time / sequence",x_options)
        plot_df=pd.DataFrame({"x":df[x],"H₂S":_num(df,y)}).dropna()
        if len(plot_df)>=1:
            fig=px.line(plot_df,x="x",y="H₂S",markers=True,title=f"H₂S concentration across {x}")
            st.plotly_chart(fig,width="stretch")
            st.download_button("⬇️ Download H₂S time-course",plot_df.to_csv(index=False).encode(),"scimantra_h2s_timecourse.csv","text/csv",width="stretch")
        if treatment_cols:
            group=st.selectbox("Optional treatment/group",treatment_cols)
            work=df[[group,x,y]].copy(); work[y]=_num(work,y); st.plotly_chart(px.line(work.dropna(),x=x,y=y,color=group,markers=True,title=f"H₂S response by {group}"),width="stretch")

    elif mode=="Influent → effluent removal":
        inflow=[c for c in h2s_cols if any(k in str(c).lower() for k in ["inlet","influent","input","initial"])]
        outflow=[c for c in h2s_cols if any(k in str(c).lower() for k in ["outlet","effluent","output","final"])]
        a=st.selectbox("Influent / inlet H₂S",inflow or h2s_cols)
        b=st.selectbox("Effluent / outlet H₂S",outflow or [c for c in h2s_cols if c!=a] or h2s_cols)
        if a==b:
            st.info("Select separate influent and effluent columns to calculate removal efficiency.")
        else:
            work=pd.DataFrame({"Influent H₂S":_num(df,a),"Effluent H₂S":_num(df,b)}).dropna()
            if len(work):
                work["Removal %"]=(work["Influent H₂S"]-work["Effluent H₂S"])/work["Influent H₂S"]*100
                st.dataframe(work.round(6),width="stretch",hide_index=True)
                m=st.columns(4); m[0].metric("Mean influent",f"{work['Influent H₂S'].mean():.5g}"); m[1].metric("Mean effluent",f"{work['Effluent H₂S'].mean():.5g}"); m[2].metric("Mean removal",f"{work['Removal %'].mean():.5g}%"); m[3].metric("N",len(work))
                st.plotly_chart(px.box(work,y="Removal %",points="all",title="H₂S removal efficiency"),width="stretch")
                if time_cols:
                    x=st.selectbox("Time / sequence",time_cols); plot=pd.DataFrame({x:df[x],"Removal %":(1-_num(df,b)/_num(df,a))*100}).replace([np.inf,-np.inf],np.nan).dropna(); st.plotly_chart(px.line(plot,x=x,y="Removal %",markers=True,title="H₂S removal over time"),width="stretch")

    elif mode=="Treatment/group comparison":
        if not treatment_cols:
            st.info("No categorical treatment/group column was detected. Add a column such as Treatment, Reactor, Condition or Group.")
        else:
            group=st.selectbox("Treatment / group",treatment_cols); response=st.selectbox("Response",h2s_cols)
            work=pd.DataFrame({group:df[group],response:_num(df,response)}).dropna(); g=work.groupby(group)[response]
            result=g.agg(N="count",Mean="mean",SD="std",Median="median",Min="min",Max="max").reset_index(); result["SEM"]=result["SD"]/np.sqrt(result["N"]); result["CV %"]=np.where(result["Mean"]!=0,result["SD"]/result["Mean"]*100,np.nan)
            st.dataframe(result.round(6),width="stretch",hide_index=True); st.plotly_chart(px.box(work,x=group,y=response,points="all",title=f"{response} by {group}"),width="stretch")
            if len(result)>=2:
                groups=[v.dropna().to_numpy() for _,v in g]
                if len(groups)==2:
                    r=stats.ttest_ind(*groups,equal_var=False); st.info(f"Welch t-test screening: t={r.statistic:.5g}, p={r.pvalue:.5g}. Use your experimental design to select the final inferential model.")
                elif len(groups)>=3:
                    r=stats.f_oneway(*groups); st.info(f"One-way ANOVA screening: F={r.statistic:.5g}, p={r.pvalue:.5g}. Check assumptions and planned contrasts before interpretation.")

    elif mode=="H₂S vs pH / operating variable":
        y=st.selectbox("H₂S response",h2s_cols); candidates=ph_cols+([c for c in numeric if c not in h2s_cols] if len(ph_cols)==0 else [])
        if not candidates: st.info("No pH or other numeric operating variable was detected.")
        else:
            x=st.selectbox("Operating variable",list(dict.fromkeys(candidates))); work=pd.DataFrame({x:_num(df,x),y:_num(df,y)}).dropna()
            if len(work)>=3:
                r=stats.linregress(work[x],work[y]); m=st.columns(4); m[0].metric("Slope",f"{r.slope:.5g}"); m[1].metric("R²",f"{r.rvalue**2:.5g}"); m[2].metric("p-value",f"{r.pvalue:.5g}"); m[3].metric("N",len(work))
                st.plotly_chart(px.scatter(work,x=x,y=y,trendline="ols",title=f"H₂S vs {x}"),width="stretch")
            else: st.info("At least three paired observations are needed for regression screening.")

    else:
        h=st.selectbox("H₂S response",h2s_cols); flow=st.selectbox("Flow rate",flow_cols or numeric); volume=st.selectbox("Reactor volume",volume_cols or numeric)
        work=pd.DataFrame({"H₂S":_num(df,h),"Flow":_num(df,flow),"Volume":_num(df,volume)}).dropna()
        if len(work):
            work["EBRT"]=work["Volume"]/work["Flow"]
            work["Loading"]=work["H₂S"]*work["Flow"]
            st.dataframe(work.round(6),width="stretch",hide_index=True)
            m=st.columns(3); m[0].metric("Mean EBRT",f"{work['EBRT'].mean():.5g}"); m[1].metric("Mean H₂S loading",f"{work['Loading'].mean():.5g}"); m[2].metric("N",len(work))
            st.caption("Loading units depend on the concentration and flow units supplied. Confirm gas/liquid basis and standard conditions before reporting.")


def _excel_bytes(df: pd.DataFrame) -> bytes:
    buf=io.BytesIO()
    with pd.ExcelWriter(buf,engine="openpyxl") as writer: df.to_excel(writer,index=False,sheet_name="Data")
    return buf.getvalue()


def render() -> None:
    st.markdown("## 📈 Data Analyzer")
    st.caption("Explore experimental datasets, replicate structure, distributions and relationships before advanced analysis.")
    st.markdown('<div class="hero"><div class="eyebrow">Research data workspace</div><h1 style="font-size:2rem;margin:0">From raw data to evidence</h1><p>Upload Excel or CSV data, inspect quality, summarize replicates, visualize patterns and export a clean working dataset.</p></div>',unsafe_allow_html=True)
    uploaded=st.file_uploader("Upload experimental data",type=["xlsx","csv"],help="Excel (.xlsx) or comma-separated values (.csv)")
    if not uploaded:
        c1,c2,c3=st.columns(3); c1.metric("Supported","Excel / CSV"); c2.metric("Quick checks","Quality + stats"); c3.metric("Visuals","Interactive"); st.info("Start by uploading your experimental dataset. Keep column names meaningful and units documented."); return
    sheet_name=None
    if uploaded.name.lower().endswith(".xlsx"):
        try:
            book,sheets=_excel_sheets(uploaded)
            if len(sheets)>1:
                scores={s:_sheet_score(pd.read_excel(book,sheet_name=s,nrows=1000)) for s in sheets}; ranked=sorted(sheets,key=lambda s:scores[s],reverse=True); default=ranked[0]
                st.markdown("### 📑 Excel worksheet"); st.caption("SciMantra prioritizes worksheets containing measurement-like data; you can override the recommendation.")
                options=[default]+[s for s in sheets if s!=default]
                sheet_name=st.selectbox("Choose worksheet",options,index=0,format_func=lambda s:f"{s}  •  {scores[s][0]} measurement columns  •  {scores[s][1]:,} numeric cells")
                if sheet_name!=default: st.info(f"Selected **{sheet_name}**. Automatic recommendation: **{default}**.")
                if scores[sheet_name][0]==0: st.warning("This worksheet appears to contain mostly text/presentation content.")
            else: sheet_name=sheets[0]
        except Exception as exc: st.error(f"Could not inspect Excel worksheets: {exc}"); return
    try: df=_load(uploaded,sheet_name)
    except Exception as exc: st.error(f"Could not read the file: {exc}"); return
    if df.empty: st.warning("The selected worksheet contains no rows."); return
    store_dataframe(df, uploaded.name, sheet_name)
    numeric=_measurement_columns(df); categorical=[c for c in df.columns if c not in numeric]; missing=int(df.isna().sum().sum()); duplicate=int(df.duplicated().sum())
    m=st.columns(5); m[0].metric("Rows",f"{len(df):,}"); m[1].metric("Columns",f"{len(df.columns):,}"); m[2].metric("Measurements",f"{len(numeric):,}"); m[3].metric("Missing cells",f"{missing:,}"); m[4].metric("Duplicate rows",f"{duplicate:,}")
    tabs=st.tabs(["🔎 Data","🧹 Quality","📊 Statistics","🧬 Replicates","🌱 H₂S Research","📈 Visualize","🔗 Relationships","⬇️ Export"])
    if any(k in str(c).lower().replace("₂","2") for c in df.columns for k in ["h2s","hydrogen sulfide","sulfide","sulphide"]):
        st.markdown("### 🧪 Continue the H₂S research workflow")
        st.caption("This dataset is available across the H₂S research pages for this browser session — no second upload is required.")
        b1, b2 = st.columns(2)
        if b1.button("Open H₂S Bioreactor Research Suite", width="stretch", key="open_h2s_suite"):
            st.switch_page("pages/20_H2S_Bioreactor_Research_Suite.py")
        if b2.button("Open H₂S Optimization & Publication", width="stretch", key="open_h2s_opt"):
            st.switch_page("pages/21_H2S_Optimization_and_Publication.py")
    with tabs[0]:
        st.markdown("### Dataset preview"); st.dataframe(df.head(100),width="stretch",height=420); st.caption(f"Showing up to 100 of {len(df):,} rows • {len(df.columns):,} columns")
        types=pd.DataFrame({"Column":df.columns,"Type":[str(df[c].dtype) for c in df.columns],"Non-null":[int(df[c].notna().sum()) for c in df.columns]}); st.dataframe(types,width="stretch",hide_index=True)
    with tabs[1]:
        quality=pd.DataFrame({"Column":df.columns,"Missing":[int(df[c].isna().sum()) for c in df.columns],"Missing %":[round(float(df[c].isna().mean()*100),2) for c in df.columns],"Unique":[int(df[c].nunique(dropna=True)) for c in df.columns],"Type":[str(df[c].dtype) for c in df.columns]}); st.dataframe(quality,width="stretch",hide_index=True)
        if missing==0 and duplicate==0: st.success("No missing cells or duplicate rows detected.")
        else:
            if missing: st.warning(f"{missing:,} missing cells detected. Decide on a scientifically justified handling method before inferential analysis.")
            if duplicate: st.warning(f"{duplicate:,} duplicate rows detected. Confirm whether they are true replicates or accidental duplicates.")
        if numeric:
            rows=[]
            for col in numeric:
                x=_num(df,col).dropna()
                if len(x)<4: rows.append({"Variable":col,"IQR flags":0,"Lower fence":np.nan,"Upper fence":np.nan}); continue
                q1,q3=x.quantile([.25,.75]); iqr=q3-q1; lo,hi=q1-1.5*iqr,q3+1.5*iqr; rows.append({"Variable":col,"IQR flags":int(((x<lo)|(x>hi)).sum()),"Lower fence":lo,"Upper fence":hi})
            st.dataframe(pd.DataFrame(rows).round(5),width="stretch",hide_index=True); st.caption("IQR flags are screening indicators, not automatic exclusion criteria.")
    with tabs[2]:
        if not numeric: st.info("No numeric columns were detected.")
        else:
            selected=st.multiselect("Variables",numeric,default=numeric[:min(5,len(numeric))]);
            if selected: result=_summary(df,selected); st.dataframe(result.round(6),width="stretch",hide_index=True); st.download_button("⬇️ Download summary CSV",result.to_csv(index=False).encode(),"scimantra_summary.csv","text/csv",width="stretch")
    with tabs[3]:
        st.markdown("### Replicate-aware group summary")
        if not numeric or not categorical: st.info("Needs at least one numeric response and one categorical/grouping column.")
        else:
            group_col=st.selectbox("Grouping variable",categorical); response=st.selectbox("Response variable",numeric); work=df[[group_col,response]].copy(); work[response]=_num(work,response); work=work.dropna(); grouped=work.groupby(group_col)[response]; result=grouped.agg(N="count",Mean="mean",SD="std",Median="median",Min="min",Max="max").reset_index(); result["SEM"]=result["SD"]/np.sqrt(result["N"]); result["CV %"]=np.where(result["Mean"]!=0,result["SD"]/result["Mean"]*100,np.nan); st.dataframe(result.round(6),width="stretch",hide_index=True); st.plotly_chart(px.box(work,x=group_col,y=response,points="all",title=f"Replicate distribution — {response} by {group_col}"),width="stretch")
    with tabs[4]: _environmental_h2s(df,numeric)
    with tabs[5]:
        if not numeric: st.info("Visualizations require at least one numeric column.")
        else:
            chart=st.selectbox("Chart",["Distribution","Box plot","Scatter plot","Time/sequence trend"])
            if chart in {"Distribution","Box plot"}:
                col=st.selectbox("Variable",numeric); p=df.copy(); p[col]=_num(p,col); fig=px.histogram(p,x=col,marginal="box",title=f"Distribution — {col}") if chart=="Distribution" else px.box(p,y=col,points="all",title=f"Box plot — {col}"); st.plotly_chart(fig,width="stretch")
            elif chart=="Scatter plot":
                x,y=st.columns(2); xc=x.selectbox("X variable",numeric); yc=y.selectbox("Y variable",numeric,index=min(1,len(numeric)-1)); p=pd.DataFrame({xc:_num(df,xc),yc:_num(df,yc)}).dropna(); st.plotly_chart(px.scatter(p,x=xc,y=yc,trendline="ols",title=f"{yc} vs {xc}"),width="stretch");
                if len(p)>=3: r=stats.linregress(p[xc],p[yc]); st.caption(f"Linear regression: slope={r.slope:.5g}, intercept={r.intercept:.5g}, R²={r.rvalue**2:.5g}, p={r.pvalue:.5g}")
            else:
                x=st.selectbox("Sequence/time column",df.columns); y=st.selectbox("Response variable",numeric); p=pd.DataFrame({x:df[x],y:_num(df,y)}).dropna(); st.plotly_chart(px.line(p,x=x,y=y,markers=True,title=f"{y} across {x}"),width="stretch")
    with tabs[6]:
        relationship_numeric = _relationship_columns(df, numeric)
        if len(relationship_numeric) < 2:
            st.info("At least two distinct, variable numeric measurements are required for relationship analysis.")
        else:
            st.markdown("### 🔗 Relationship analysis")
            st.caption("SciMantra excludes Unnamed:* Excel artifacts, constants, repeated .1/.2 worksheet calculation columns, and exact duplicate series before correlation.")
            default_relationship = relationship_numeric[:min(8, len(relationship_numeric))]
            selected_rel = st.multiselect("Variables for correlation", relationship_numeric, default=default_relationship, key="relationship_variables")
            method = st.radio("Correlation method", ["Pearson", "Spearman"], horizontal=True, key="correlation_method")
            if len(selected_rel) < 2:
                st.info("Select at least two variables.")
            else:
                corr_data = df[selected_rel].apply(pd.to_numeric, errors="coerce")
                corr = corr_data.corr(method=method.lower(), min_periods=3)
                fig = px.imshow(corr, text_auto=".2f", aspect="auto", zmin=-1, zmax=1, title=f"{method} correlation matrix")
                fig.update_layout(height=max(520, 45 * len(selected_rel)), margin=dict(l=20, r=20, t=70, b=20))
                st.plotly_chart(fig, width="stretch")
                st.dataframe(corr.round(4), width="stretch")
                st.caption(f"Showing {len(selected_rel)} distinct analysis variables. Correlations use pairwise complete observations with a minimum of 3 paired values; interpret small samples cautiously.")

            st.markdown("### 🧪 H₂S research relationships")
            names = {str(c).lower().replace("₂", "2"): c for c in df.columns}
            def pick(keys):
                for key, col in names.items():
                    if any(k in key for k in keys):
                        return col
                return None

            inlet = pick(["inlet h2s", "influent h2s", "input h2s", "initial h2s"])
            outlet = pick(["outlet h2s", "effluent h2s", "output h2s", "final h2s"])
            removal = pick(["removal efficiency", "removal %", "h2s removal"])
            load = pick(["inlet h2s load", "h2s loading", "loading"])
            ebrt = pick(["ebrt"])
            ph = pick(["pH", "ph"])
            x_candidates = []
            if inlet and outlet: x_candidates.append(("Inlet H₂S vs Outlet H₂S", inlet, outlet))
            if load and removal: x_candidates.append(("Inlet H₂S loading vs Removal efficiency", load, removal))
            if ebrt and removal: x_candidates.append(("EBRT vs Removal efficiency", ebrt, removal))
            if ph and removal: x_candidates.append(("pH vs Removal efficiency", ph, removal))

            if not x_candidates:
                st.info("No complete H₂S relationship pair was detected automatically. Use the correlation selector above or rename columns with clear H₂S, loading, EBRT and pH labels.")
            else:
                label, xcol, ycol = st.selectbox("Research relationship", x_candidates, format_func=lambda z: z[0], key="h2s_relationship_pair")
                work = pd.DataFrame({"X": pd.to_numeric(df[xcol], errors="coerce"), "Y": pd.to_numeric(df[ycol], errors="coerce")}).dropna()
                if len(work) >= 3 and work["X"].nunique() >= 2:
                    r = stats.linregress(work["X"], work["Y"])
                    c1,c2,c3,c4 = st.columns(4)
                    c1.metric("N", len(work)); c2.metric("Pearson r", f"{r.rvalue:.4f}"); c3.metric("R²", f"{r.rvalue**2:.4f}"); c4.metric("p-value", f"{r.pvalue:.4g}")
                    plot = px.scatter(work, x="X", y="Y", trendline="ols", title=label)
                    plot.update_layout(height=500)
                    st.plotly_chart(plot, width="stretch")
                    st.caption(f"X = {xcol} • Y = {ycol}. Regression is an association screen, not proof of causality or a global optimum.")
                    result = pd.DataFrame([{
                        "Relationship": label, "X variable": xcol, "Y variable": ycol, "N": len(work),
                        "Pearson r": r.rvalue, "R²": r.rvalue**2, "Slope": r.slope,
                        "Intercept": r.intercept, "p-value": r.pvalue, "Std. error": r.stderr
                    }])
                    st.dataframe(result.round(6), width="stretch", hide_index=True)
                    st.download_button("⬇️ Download relationship result", result.to_csv(index=False).encode("utf-8"), "scimantra_h2s_relationship.csv", "text/csv", width="stretch")
                else:
                    st.info("At least three paired observations and variation in X are required for regression screening.")
    with tabs[7]:
        st.markdown("### Export"); st.write("Download the original dataset or a selected working subset for your next analysis step."); cols=st.multiselect("Columns to export",list(df.columns),default=list(df.columns)); export_df=df[cols] if cols else df; _download(export_df); st.download_button("⬇️ Download Excel",_excel_bytes(export_df),"scimantra_data.xlsx","application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",width="stretch"); st.caption("SciMantra does not silently impute, delete or transform observations. Any cleaning decision should be documented and scientifically justified.")
