import pandas as pd
import streamlit as st

from src.scimantra.entitlements import require

st.title("🚀 SciMantra Pro Workspace")
st.caption("Research workspace for data summaries, interpretation, figures and publication-ready report drafts.")

if not require("pro_workspace"):
    st.stop()

if "project_name" not in st.session_state:
    st.session_state.project_name = "My Research Project"
if "notes" not in st.session_state:
    st.session_state.notes = ""

with st.sidebar:
    st.subheader("Workspace")
    st.session_state.project_name = st.text_input("Project name", st.session_state.project_name)

section = st.selectbox("Workspace module", ["Project Dashboard", "Dataset Summary", "Research Notes", "Report Builder", "Pro Roadmap"])

if section == "Project Dashboard":
    st.subheader(st.session_state.project_name)
    c1, c2, c3 = st.columns(3)
    c1.metric("Workspace", "Pro")
    c2.metric("Data privacy", "Session only")
    c3.metric("Reporting", "Ready")
    st.info("Recommended workflow: upload → validate → summarize → analyze → interpret → report → export.")
    st.markdown("### Available research pipeline")
    st.markdown("1. Upload CSV/XLSX data.\n2. Review sample count, variables and missing values.\n3. Generate descriptive statistics and a compact summary table.\n4. Add interpretation and limitations.\n5. Export an editable report draft.")

elif section == "Dataset Summary":
    st.subheader("📊 Dataset Summary")
    uploaded = st.file_uploader("Upload CSV or Excel dataset", type=["csv", "xlsx", "xls"])
    if uploaded:
        try:
            df = pd.read_csv(uploaded) if uploaded.name.lower().endswith(".csv") else pd.read_excel(uploaded)
            st.session_state.report_df = df
            st.success(f"Loaded {len(df):,} rows × {len(df.columns):,} columns.")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Rows", f"{len(df):,}")
            c2.metric("Columns", f"{len(df.columns):,}")
            c3.metric("Missing cells", f"{int(df.isna().sum().sum()):,}")
            c4.metric("Numeric variables", f"{len(df.select_dtypes(include='number').columns):,}")
            st.dataframe(df.head(100), width="stretch", hide_index=True)
            numeric = df.select_dtypes(include="number")
            if not numeric.empty:
                st.markdown("### Descriptive statistics")
                summary = numeric.describe().T.reset_index().rename(columns={"index": "Variable"})
                summary["SEM"] = numeric.sem().values
                summary["CV %"] = (numeric.std() / numeric.mean().replace(0, pd.NA) * 100).values
                st.dataframe(summary.round(5), width="stretch", hide_index=True)
                st.download_button("⬇️ Download statistics CSV", summary.to_csv(index=False).encode("utf-8"), "scimantra_descriptive_statistics.csv", "text/csv")
        except Exception as exc:
            st.error(f"Could not read the dataset: {exc}")
    else:
        st.info("Upload a dataset to generate an automatic descriptive summary. Data remains session-scoped until cloud persistence is configured.")

elif section == "Research Notes":
    st.subheader("📝 Research Notes")
    st.session_state.notes = st.text_area("Interpretation, observations, limitations or manuscript notes", st.session_state.notes, height=300)
    st.download_button("⬇️ Download notes", st.session_state.notes.encode("utf-8"), "scimantra_research_notes.txt", "text/plain")

elif section == "Report Builder":
    st.subheader("📄 Publication-Ready Report Draft")
    title = st.text_input("Report title", st.session_state.project_name)
    author = st.text_input("Author / laboratory")
    objective = st.text_area("Research objective", height=100)
    methods = st.text_area("Methods / experimental design", height=140)
    results = st.text_area("Results and interpretation", height=180)
    conclusion = st.text_area("Conclusion", height=120)
    limitations = st.text_area("Limitations", height=120)
    df = st.session_state.get("report_df")
    dataset_section = "No dataset summary attached."
    if isinstance(df, pd.DataFrame):
        numeric = df.select_dtypes(include="number")
        dataset_section = f"Dataset: {len(df)} observations and {len(df.columns)} variables. Missing cells: {int(df.isna().sum().sum())}. Numeric variables: {len(numeric.columns)}."
        if not numeric.empty:
            means = numeric.mean().round(4).to_dict()
            dataset_section += "\nNumeric-variable means: " + "; ".join(f"{k}={v}" for k, v in means.items()) + "."
    generated = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")
    report = f"""{title}\n{'=' * max(10, len(title))}\n\nAuthor/Laboratory: {author}\nGenerated: {generated}\n\nABSTRACT / SUMMARY\n{results}\n\n1. RESEARCH OBJECTIVE\n{objective}\n\n2. METHODS\n{methods}\n\n3. DATASET SUMMARY\n{dataset_section}\n\n4. RESULTS AND INTERPRETATION\n{results}\n\n5. CONCLUSION\n{conclusion}\n\n6. LIMITATIONS\n{limitations}\n\n7. RESEARCH NOTES\n{st.session_state.notes}\n\nSciMantra Research Tools\n"""
    st.markdown("### Report preview")
    st.text_area("Preview", report, height=500)
    st.download_button("⬇️ Export report (.txt)", report.encode("utf-8"), "scimantra_research_report.txt", "text/plain")
    st.caption("This generates an editable research draft. Verify calculations, assumptions, statistical choices and journal requirements before submission.")

else:
    st.subheader("Production Roadmap")
    roadmap = pd.DataFrame([
        ["Research workspace", "Live", "Project notes, dataset summary and report drafting"],
        ["Advanced experimental analysis", "Live", "Replicate-aware analysis and figures"],
        ["TEA & LCA", "Live", "Economic and sustainability screening"],
        ["Dataset-aware report builder", "Live", "Automatic descriptive summary and export"],
        ["Secure accounts", "Live (optional)", "Supabase-ready account layer"],
        ["Cloud projects", "Live (optional)", "Supabase-backed project persistence"],
        ["Subscriptions", "Ready", "Entitlement layer + provider-neutral checkout architecture"],
        ["AI research assistant", "Pro", "Requires configured AI API key"],
        ["Similarity checker", "Not included", "Requires licensed reference corpus/provider and validation"],
    ], columns=["Capability", "Status", "Implementation note"])
    st.dataframe(roadmap, width="stretch", hide_index=True)
    st.warning("Do not market similarity or AI-detection functionality as equivalent to Turnitin or another proprietary service without the required corpus/provider and validation.")
