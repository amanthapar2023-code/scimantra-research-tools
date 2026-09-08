import streamlit as st
import pandas as pd
from src.scimantra.results_interpreter import summarize_numeric, compare_groups, interpretation_flags

st.set_page_config(page_title="Results Interpreter | SciMantra", page_icon="📊", layout="wide")
st.title("📊 Results Interpreter")
st.caption("Upload your actual data and turn it into transparent descriptive evidence and effect summaries.")

uploaded = st.file_uploader("Upload CSV data", type=["csv"])
if uploaded is None:
    st.info("Start with a CSV containing one row per observation/experimental unit. No data means no result will be generated.")
    st.stop()

df = pd.read_csv(uploaded)
st.success(f"Loaded {len(df):,} rows × {len(df.columns):,} columns")
st.dataframe(df.head(20), width="stretch", hide_index=True)

numeric = list(df.select_dtypes(include="number").columns)
if numeric:
    st.subheader("Descriptive statistics")
    summary = summarize_numeric(df)
    st.dataframe(summary, width="stretch", hide_index=True)
else:
    summary = pd.DataFrame()

st.subheader("Two-group effect summary")
if numeric and len(df.columns) > 1:
    outcome = st.selectbox("Outcome", numeric)
    group_candidates = [c for c in df.columns if c != outcome]
    group = st.selectbox("Group / condition", group_candidates)
    comparison = compare_groups(df, outcome, group)
    if comparison.get("status") == "OK":
        a,b,c,d = st.columns(4)
        a.metric(comparison["group_a"], f"n={comparison['n_a']}")
        b.metric(comparison["group_b"], f"n={comparison['n_b']}")
        c.metric("Mean difference", f"{comparison['difference']:.4g}")
        d.metric("Standardized difference", f"{comparison['standardized_difference']:.4g}" if comparison['standardized_difference'] == comparison['standardized_difference'] else "NA")
    else:
        st.warning(comparison.get("status", "Unable to compare groups."))
else:
    comparison = {"status": "NO_COMPARISON"}

st.subheader("🧠 Interpretation guardrails")
for flag in interpretation_flags(summary, comparison):
    st.write("• " + flag)

st.download_button("⬇️ Export descriptive summary", summary.to_csv(index=False).encode(), "scimantra_results_summary.csv", "text/csv", width="stretch")
st.warning("Scientific integrity rule: this page reports calculations from the uploaded dataset. It does not invent results, infer causality, or replace domain-specific statistical review.")
