from __future__ import annotations

import io
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from scipy import stats


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
    rows = []
    for col in selected:
        x = pd.to_numeric(df[col], errors="coerce").dropna().to_numpy(dtype=float)
        n = len(x)
        mean = float(np.mean(x)) if n else np.nan
        sd = float(np.std(x, ddof=1)) if n > 1 else np.nan
        sem = sd / np.sqrt(n) if n > 1 else np.nan
        cv = (sd / mean * 100) if n > 1 and mean != 0 else np.nan
        rows.append({"Variable": col, "N": n, "Mean": mean, "SD": sd, "SEM": sem, "CV %": cv, "Median": float(np.median(x)) if n else np.nan, "Min": float(np.min(x)) if n else np.nan, "Max": float(np.max(x)) if n else np.nan})
    return pd.DataFrame(rows)


def _measurement_columns(df: pd.DataFrame) -> list[str]:
    """Detect numeric columns, including numbers imported as text."""
    numeric = []
    for col in df.columns:
        converted = pd.to_numeric(df[col], errors="coerce")
        original_nonnull = int(df[col].notna().sum())
        numeric_nonnull = int(converted.notna().sum())
        if original_nonnull and numeric_nonnull / original_nonnull >= 0.8:
            numeric.append(col)
    return numeric


def _sheet_score(df: pd.DataFrame) -> tuple[int, int, int]:
    measurement_cols = _measurement_columns(df)
    numeric_cells = sum(int(pd.to_numeric(df[c], errors="coerce").notna().sum()) for c in measurement_cols)
    nonempty = int(df.notna().any(axis=1).sum())
    return len(measurement_cols), numeric_cells, nonempty


def render() -> None:
    st.markdown("## 📈 Data Analyzer")
    st.caption("Explore experimental datasets, replicate structure, distributions and relationships before advanced analysis.")
    st.markdown('<div class="hero"><div class="eyebrow">Research data workspace</div><h1 style="font-size:2rem;margin:0">From raw data to evidence</h1><p>Upload Excel or CSV data, inspect quality, summarize replicates, visualize patterns and export a clean working dataset.</p></div>', unsafe_allow_html=True)

    uploaded = st.file_uploader("Upload experimental data", type=["xlsx", "csv"], help="Excel (.xlsx) or comma-separated values (.csv)")
    if not uploaded:
        c1, c2, c3 = st.columns(3)
        c1.metric("Supported", "Excel / CSV")
        c2.metric("Quick checks", "Quality + stats")
        c3.metric("Visuals", "Interactive")
        st.info("Start by uploading your experimental dataset. Keep column names meaningful and units documented.")
        return

    sheet_name = None
    if uploaded.name.lower().endswith(".xlsx"):
        try:
            book, sheets = _excel_sheets(uploaded)
            if len(sheets) > 1:
                sheet_scores = {}
                for sheet in sheets:
                    candidate = pd.read_excel(book, sheet_name=sheet, nrows=1000)
                    sheet_scores[sheet] = _sheet_score(candidate)
                ranked = sorted(sheets, key=lambda s: sheet_scores[s], reverse=True)
                default_sheet = ranked[0]
                st.markdown("### 📑 Excel worksheet")
                st.caption("SciMantra automatically prioritizes worksheets containing measurement-like numeric data. You can change the selection at any time.")
                options = [default_sheet] + [s for s in sheets if s != default_sheet]
                def _fmt(s):
                    cols, cells, rows = sheet_scores[s]
                    return f"{s}  •  {cols} measurement columns  •  {cells:,} numeric cells"
                sheet_name = st.selectbox("Choose worksheet", options, index=0, format_func=_fmt)
                if sheet_name != default_sheet:
                    st.info(f"Selected worksheet: **{sheet_name}**. SciMantra's automatic recommendation was **{default_sheet}** because it contained the strongest measurement signal.")
                if sheet_scores[sheet_name][0] == 0:
                    st.warning("This worksheet appears to contain mostly text/presentation content. Select the worksheet containing your experimental measurements.")
            else:
                sheet_name = sheets[0]
        except Exception as exc:
            st.error(f"Could not inspect Excel worksheets: {exc}")
            return

    try:
        df = _load(uploaded, sheet_name)
    except Exception as exc:
        st.error(f"Could not read the file: {exc}")
        return

    if df.empty:
        st.warning("The selected worksheet contains no rows.")
        return

    numeric = _measurement_columns(df)
    categorical = [c for c in df.columns if c not in numeric]
    missing = int(df.isna().sum().sum())
    duplicate = int(df.duplicated().sum())

    m = st.columns(5)
    m[0].metric("Rows", f"{len(df):,}")
    m[1].metric("Columns", f"{len(df.columns):,}")
    m[2].metric("Measurements", f"{len(numeric):,}")
    m[3].metric("Missing cells", f"{missing:,}")
    m[4].metric("Duplicate rows", f"{duplicate:,}")

    if not numeric:
        st.warning("No measurement columns were detected. For H₂S research, select the worksheet containing concentration, time, pH or other numeric observations.")

    tabs = st.tabs(["🔎 Data", "🧹 Quality", "📊 Statistics", "🧬 Replicates", "📈 Visualize", "🔗 Relationships", "⬇️ Export"])

    with tabs[0]:
        st.markdown("### Dataset preview")
        st.dataframe(df.head(100), width="stretch", height=420)
        st.caption(f"Showing up to 100 of {len(df):,} rows • {len(df.columns):,} columns")
        st.markdown("### Column types")
        types = pd.DataFrame({"Column": df.columns, "Type": [str(df[c].dtype) for c in df.columns], "Non-null": [int(df[c].notna().sum()) for c in df.columns]})
        st.dataframe(types, width="stretch", hide_index=True)

    with tabs[1]:
        st.markdown("### Data quality report")
        quality = pd.DataFrame({"Column": df.columns, "Missing": [int(df[c].isna().sum()) for c in df.columns], "Missing %": [round(float(df[c].isna().mean() * 100), 2) for c in df.columns], "Unique": [int(df[c].nunique(dropna=True)) for c in df.columns], "Type": [str(df[c].dtype) for c in df.columns]})
        st.dataframe(quality, width="stretch", hide_index=True)
        if missing == 0 and duplicate == 0: st.success("No missing cells or duplicate rows detected.")
        else:
            if missing: st.warning(f"{missing:,} missing cells detected. Decide on a scientifically justified handling method before inferential analysis.")
            if duplicate: st.warning(f"{duplicate:,} duplicate rows detected. Confirm whether they are true replicates or accidental duplicates.")
        if numeric:
            st.markdown("### Distribution screening")
            outlier_rows = []
            for col in numeric:
                x = pd.to_numeric(df[col], errors="coerce").dropna()
                if len(x) < 4:
                    outlier_rows.append({"Variable": col, "IQR flags": 0, "Lower fence": np.nan, "Upper fence": np.nan}); continue
                q1, q3 = x.quantile([0.25, 0.75]); iqr = q3 - q1; lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
                outlier_rows.append({"Variable": col, "IQR flags": int(((x < lo) | (x > hi)).sum()), "Lower fence": lo, "Upper fence": hi})
            st.dataframe(pd.DataFrame(outlier_rows).round(5), width="stretch", hide_index=True)
            st.caption("IQR flags are screening indicators, not automatic exclusion criteria. Investigate experimental context before removing observations.")

    with tabs[2]:
        if not numeric: st.info("No numeric columns were detected.")
        else:
            selected = st.multiselect("Variables", numeric, default=numeric[:min(5, len(numeric))])
            if selected:
                result = _summary(df, selected)
                st.dataframe(result.round(6), width="stretch", hide_index=True)
                st.download_button("⬇️ Download summary CSV", result.to_csv(index=False).encode("utf-8"), "scimantra_summary.csv", "text/csv", width="stretch")

    with tabs[3]:
        st.markdown("### Replicate-aware group summary")
        if not numeric or not categorical: st.info("To summarize replicates by group, the dataset needs at least one numeric response and one categorical/grouping column.")
        else:
            group_col = st.selectbox("Grouping variable", categorical)
            response = st.selectbox("Response variable", numeric)
            grouped = df[[group_col, response]].dropna().assign(**{response: lambda d: pd.to_numeric(d[response], errors="coerce")}).dropna().groupby(group_col)[response]
            result = grouped.agg(N="count", Mean="mean", SD="std", Median="median", Min="min", Max="max").reset_index()
            result["SEM"] = result["SD"] / np.sqrt(result["N"]); result["CV %"] = np.where(result["Mean"] != 0, result["SD"] / result["Mean"] * 100, np.nan)
            result = result[[group_col, "N", "Mean", "SD", "SEM", "CV %", "Median", "Min", "Max"]]
            st.dataframe(result.round(6), width="stretch", hide_index=True)
            plot_df = df[[group_col, response]].copy(); plot_df[response] = pd.to_numeric(plot_df[response], errors="coerce")
            st.plotly_chart(px.box(plot_df.dropna(), x=group_col, y=response, points="all", title=f"Replicate distribution — {response} by {group_col}"), width="stretch")
            st.caption("N is the number of non-missing observations per group. Interpret biological and technical replicates according to your experimental design.")

    with tabs[4]:
        if not numeric: st.info("Visualizations require at least one numeric column.")
        else:
            chart = st.selectbox("Chart", ["Distribution", "Box plot", "Scatter plot", "Time/sequence trend"])
            if chart in {"Distribution", "Box plot"}:
                col = st.selectbox("Variable", numeric); plot_df = df.copy(); plot_df[col] = pd.to_numeric(plot_df[col], errors="coerce")
                fig = px.histogram(plot_df, x=col, marginal="box", title=f"Distribution — {col}") if chart == "Distribution" else px.box(plot_df, y=col, points="all", title=f"Box plot — {col}")
                st.plotly_chart(fig, width="stretch")
            elif chart == "Scatter plot":
                xcol, ycol = st.columns(2); x = xcol.selectbox("X variable", numeric); y = ycol.selectbox("Y variable", numeric, index=min(1, len(numeric)-1)); plot_df = df[[x,y]].copy(); plot_df[x]=pd.to_numeric(plot_df[x],errors="coerce"); plot_df[y]=pd.to_numeric(plot_df[y],errors="coerce")
                clean=plot_df.dropna(); st.plotly_chart(px.scatter(clean, x=x, y=y, trendline="ols", title=f"{y} vs {x}"), width="stretch")
                if len(clean) >= 3:
                    r=stats.linregress(clean[x],clean[y]); st.caption(f"Linear regression: slope={r.slope:.5g}, intercept={r.intercept:.5g}, R²={r.rvalue**2:.5g}, p={r.pvalue:.5g}")
            else:
                xcol, ycol = st.columns(2); x = xcol.selectbox("Sequence/time column", df.columns); y = ycol.selectbox("Response variable", numeric); plot_df=df[[x,y]].copy(); plot_df[y]=pd.to_numeric(plot_df[y],errors="coerce"); st.plotly_chart(px.line(plot_df.dropna(), x=x, y=y, markers=True, title=f"{y} across {x}"), width="stretch")

    with tabs[5]:
        if len(numeric) < 2: st.info("At least two measurement columns are required for relationship analysis.")
        else:
            method = st.radio("Correlation method", ["Pearson", "Spearman"], horizontal=True); work=df[numeric].apply(pd.to_numeric,errors="coerce"); corr=work.corr(method="pearson" if method=="Pearson" else "spearman")
            st.plotly_chart(px.imshow(corr, text_auto=".2f", aspect="auto", title=f"{method} correlation matrix"), width="stretch"); st.dataframe(corr.round(4), width="stretch")

    with tabs[6]:
        st.markdown("### Export")
        st.write("Download the original dataset or a selected working subset for your next analysis step.")
        cols = st.multiselect("Columns to export", list(df.columns), default=list(df.columns)); export_df=df[cols] if cols else df
        _download(export_df); st.download_button("⬇️ Download Excel", _excel_bytes(export_df), "scimantra_data.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", width="stretch")
        st.caption("SciMantra does not silently impute, delete or transform observations. Any cleaning decision should be documented and scientifically justified.")


def _excel_bytes(df: pd.DataFrame) -> bytes:
    buf=io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer: df.to_excel(writer,index=False,sheet_name="Data")
    return buf.getvalue()
