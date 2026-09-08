from __future__ import annotations

import io
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from scipy import stats


def _load(uploaded):
    if uploaded.name.lower().endswith(".csv"):
        return pd.read_csv(uploaded)
    return pd.read_excel(uploaded)


def _download(df: pd.DataFrame):
    st.download_button(
        "⬇️ Download cleaned/selected data",
        df.to_csv(index=False).encode("utf-8"),
        "scimantra_data.csv",
        "text/csv",
        width="stretch",
    )


def render() -> None:
    st.markdown("## 📈 Data Analyzer")
    st.caption("Explore experimental datasets, replicate structure, distributions and relationships before advanced analysis.")
    st.markdown(
        '<div class="hero"><div class="eyebrow">Research data workspace</div>'
        '<h1 style="font-size:2rem;margin:0">From raw data to evidence</h1>'
        '<p>Upload Excel or CSV data, inspect quality, summarize replicates, visualize patterns and export a clean working dataset.</p></div>',
        unsafe_allow_html=True,
    )

    uploaded = st.file_uploader("Upload experimental data", type=["xlsx", "csv"], help="Excel (.xlsx) or comma-separated values (.csv)")
    if not uploaded:
        c1, c2, c3 = st.columns(3)
        c1.metric("Supported", "Excel / CSV")
        c2.metric("Quick checks", "Quality + stats")
        c3.metric("Visuals", "Interactive")
        st.info("Start by uploading your experimental dataset. Keep column names meaningful and units documented.")
        return

    try:
        df = _load(uploaded)
    except Exception as exc:
        st.error(f"Could not read the file: {exc}")
        return

    if df.empty:
        st.warning("The uploaded dataset contains no rows.")
        return

    numeric = df.select_dtypes(include=np.number).columns.tolist()
    categorical = [c for c in df.columns if c not in numeric]
    missing = int(df.isna().sum().sum())
    duplicate = int(df.duplicated().sum())

    m = st.columns(5)
    m[0].metric("Rows", f"{len(df):,}")
    m[1].metric("Columns", f"{len(df.columns):,}")
    m[2].metric("Numeric", f"{len(numeric):,}")
    m[3].metric("Missing cells", f"{missing:,}")
    m[4].metric("Duplicate rows", f"{duplicate:,}")

    tabs = st.tabs(["🔎 Data", "🧹 Quality", "📊 Statistics", "📈 Visualize", "🔗 Relationships", "⬇️ Export"])

    with tabs[0]:
        st.markdown("### Dataset preview")
        st.dataframe(df.head(100), width="stretch", height=420)
        st.caption(f"Showing up to 100 of {len(df):,} rows • {len(df.columns):,} columns")
        st.markdown("### Column types")
        types = pd.DataFrame({"Column": df.columns, "Type": [str(df[c].dtype) for c in df.columns], "Non-null": [int(df[c].notna().sum()) for c in df.columns]})
        st.dataframe(types, width="stretch", hide_index=True)

    with tabs[1]:
        st.markdown("### Data quality report")
        quality = pd.DataFrame({
            "Column": df.columns,
            "Missing": [int(df[c].isna().sum()) for c in df.columns],
            "Missing %": [round(float(df[c].isna().mean() * 100), 2) for c in df.columns],
            "Unique": [int(df[c].nunique(dropna=True)) for c in df.columns],
            "Type": [str(df[c].dtype) for c in df.columns],
        })
        st.dataframe(quality, width="stretch", hide_index=True)
        if missing == 0 and duplicate == 0:
            st.success("No missing cells or duplicate rows detected.")
        else:
            if missing: st.warning(f"{missing:,} missing cells detected. Decide on a scientifically justified handling method before inferential analysis.")
            if duplicate: st.warning(f"{duplicate:,} duplicate rows detected. Confirm whether they are true replicates or accidental duplicates.")

    with tabs[2]:
        if not numeric:
            st.info("No numeric columns were detected.")
        else:
            selected = st.multiselect("Variables", numeric, default=numeric[: min(5, len(numeric))])
            if selected:
                rows = []
                for col in selected:
                    x = pd.to_numeric(df[col], errors="coerce").dropna().to_numpy(dtype=float)
                    mean = float(np.mean(x)) if len(x) else np.nan
                    sd = float(np.std(x, ddof=1)) if len(x) > 1 else np.nan
                    sem = sd / np.sqrt(len(x)) if len(x) > 1 else np.nan
                    cv = (sd / mean * 100) if len(x) > 1 and mean != 0 else np.nan
                    rows.append({"Variable": col, "N": len(x), "Mean": mean, "SD": sd, "SEM": sem, "CV %": cv, "Median": float(np.median(x)) if len(x) else np.nan, "Min": float(np.min(x)) if len(x) else np.nan, "Max": float(np.max(x)) if len(x) else np.nan})
                st.dataframe(pd.DataFrame(rows).round(6), width="stretch", hide_index=True)
                st.download_button("⬇️ Download summary CSV", pd.DataFrame(rows).to_csv(index=False).encode("utf-8"), "scimantra_summary.csv", "text/csv", width="stretch")

    with tabs[3]:
        if not numeric:
            st.info("Visualizations require at least one numeric column.")
        else:
            chart = st.selectbox("Chart", ["Distribution", "Box plot", "Scatter plot", "Time/sequence trend"])
            if chart in {"Distribution", "Box plot"}:
                col = st.selectbox("Variable", numeric)
                if chart == "Distribution":
                    fig = px.histogram(df, x=col, marginal="box", title=f"Distribution — {col}")
                else:
                    fig = px.box(df, y=col, points="all", title=f"Box plot — {col}")
                st.plotly_chart(fig, width="stretch")
            elif chart == "Scatter plot":
                xcol, ycol = st.columns(2)
                x = xcol.selectbox("X variable", numeric)
                y = ycol.selectbox("Y variable", numeric, index=min(1, len(numeric)-1))
                fig = px.scatter(df, x=x, y=y, trendline="ols", title=f"{y} vs {x}")
                st.plotly_chart(fig, width="stretch")
                clean = df[[x, y]].dropna()
                if len(clean) >= 3:
                    r = stats.linregress(clean[x], clean[y])
                    st.caption(f"Linear regression: slope={r.slope:.5g}, intercept={r.intercept:.5g}, R²={r.rvalue**2:.5g}, p={r.pvalue:.5g}")
            else:
                xcol, ycol = st.columns(2)
                x = xcol.selectbox("Sequence/time column", df.columns)
                y = ycol.selectbox("Response variable", numeric)
                fig = px.line(df, x=x, y=y, markers=True, title=f"{y} across {x}")
                st.plotly_chart(fig, width="stretch")

    with tabs[4]:
        if len(numeric) < 2:
            st.info("At least two numeric columns are required for relationship analysis.")
        else:
            method = st.radio("Correlation method", ["Pearson", "Spearman"], horizontal=True)
            corr = df[numeric].corr(method="pearson" if method == "Pearson" else "spearman")
            fig = px.imshow(corr, text_auto=".2f", aspect="auto", title=f"{method} correlation matrix")
            st.plotly_chart(fig, width="stretch")
            st.dataframe(corr.round(4), width="stretch")

    with tabs[5]:
        st.markdown("### Export")
        st.write("Download the original dataset or a selected working subset for your next analysis step.")
        cols = st.multiselect("Columns to export", list(df.columns), default=list(df.columns))
        if cols:
            _download(df[cols])
        st.download_button("⬇️ Download Excel", _excel_bytes(df[cols] if cols else df), "scimantra_data.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", width="stretch")
        st.caption("SciMantra does not silently impute, delete or transform observations. Any cleaning decision should be documented and scientifically justified.")


def _excel_bytes(df: pd.DataFrame) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Data")
    return buf.getvalue()
