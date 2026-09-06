from datetime import datetime
import io

import pandas as pd
import streamlit as st

st.set_page_config(page_title="SciMantra Research Report", page_icon="📄", layout="wide")
st.title("📄 Automated Research Report Builder")
st.caption("Build a structured, editable research report from your dataset and analysis outputs.")

if "report_data" not in st.session_state:
    st.session_state.report_data = None
if "report_stats" not in st.session_state:
    st.session_state.report_stats = None

uploaded = st.file_uploader("Upload CSV or Excel dataset", type=["csv", "xlsx", "xls"])
if uploaded:
    try:
        df = pd.read_csv(uploaded) if uploaded.name.lower().endswith(".csv") else pd.read_excel(uploaded)
        st.session_state.report_data = df
    except Exception as exc:
        st.error(f"Could not read dataset: {exc}")

df = st.session_state.report_data
if df is not None:
    numeric = df.select_dtypes(include="number")
    stats_df = numeric.describe().T if not numeric.empty else pd.DataFrame()
    st.session_state.report_stats = stats_df
    c1, c2, c3 = st.columns(3)
    c1.metric("Observations", f"{len(df):,}")
    c2.metric("Variables", f"{len(df.columns):,}")
    c3.metric("Missing cells", f"{int(df.isna().sum().sum()):,}")

st.subheader("Report information")
title = st.text_input("Manuscript / project title", "Research Study")
author = st.text_input("Author / laboratory", "")
objective = st.text_area("Objective", "")
methods = st.text_area("Methods", "Describe experimental design, sampling, replicates, measurements and statistical methods.")
results = st.text_area("Results / interpretation", "", height=180)
discussion = st.text_area("Discussion", "", height=180)
conclusion = st.text_area("Conclusion", "", height=140)
limitations = st.text_area("Limitations", "", height=120)

if st.button("Generate complete report", type="primary"):
    if df is None:
        st.warning("Upload a dataset first.")
    else:
        numeric = df.select_dtypes(include="number")
        missing = int(df.isna().sum().sum())
        lines = [
            title,
            "=" * len(title),
            f"Author / laboratory: {author or 'Not specified'}",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "ABSTRACT / SUMMARY",
            results or "Draft this section after reviewing the statistical evidence.",
            "",
            "1. OBJECTIVE",
            objective or "Not specified.",
            "",
            "2. METHODS",
            methods or "Not specified.",
            "",
            "3. DATASET AND QUALITY",
            f"The dataset contained {len(df):,} observations and {len(df.columns):,} variables. "
            f"There were {missing:,} missing cells. {len(numeric.columns):,} numeric variables were identified.",
        ]
        if not numeric.empty:
            lines += ["", "Descriptive statistics:"]
            for name, row in numeric.describe().T.iterrows():
                lines.append(f"- {name}: n={int(row['count'])}, mean={row['mean']:.6g}, SD={row['std']:.6g}, median={row['50%']:.6g}, range={row['min']:.6g}–{row['max']:.6g}")
        lines += [
            "",
            "4. RESULTS",
            results or "Not specified.",
            "",
            "5. DISCUSSION",
            discussion or "Not specified.",
            "",
            "6. CONCLUSION",
            conclusion or "Not specified.",
            "",
            "7. LIMITATIONS",
            limitations or "Not specified.",
            "",
            "SCIENTIFIC REVIEW NOTE",
            "This report is an editable draft. Verify all calculations, assumptions, experimental design, "
            "statistical choices, biological interpretations, citations and journal-specific formatting before submission.",
        ]
        report = "\n".join(lines)
        st.session_state.generated_report = report

report = st.session_state.get("generated_report")
if report:
    st.subheader("Report preview")
    st.text_area("Editable manuscript draft", report, height=600)
    st.download_button("⬇️ Download TXT report", report.encode("utf-8"), "scimantra_research_report.txt", "text/plain")
    st.info("For journal submission, copy the reviewed content into your target manuscript template and apply the journal's required structure, references and figure/table rules.")
