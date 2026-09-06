import json
import urllib.request
from datetime import datetime

import numpy as np
import pandas as pd
import streamlit as st

from src.scimantra.entitlements import require

st.title("🤖 SciMantra AI Research Assistant")
st.caption("Evidence-first research assistance: calculated findings stay separate from suggested interpretation.")

if not require("ai_assistant"):
    st.stop()

if "ai_df" not in st.session_state:
    st.session_state.ai_df = None

uploaded = st.file_uploader("Upload CSV or Excel dataset", type=["csv", "xlsx", "xls"])
if uploaded:
    try:
        st.session_state.ai_df = pd.read_csv(uploaded) if uploaded.name.lower().endswith(".csv") else pd.read_excel(uploaded)
    except Exception as exc:
        st.error(f"Could not read the dataset: {exc}")

_df = st.session_state.ai_df

if _df is not None:
    st.success(f"Dataset loaded: {_df.shape[0]:,} rows × {_df.shape[1]:,} columns")
    numeric = _df.select_dtypes(include="number")
    missing = int(_df.isna().sum().sum())
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Observations", f"{len(_df):,}")
    c2.metric("Variables", f"{len(_df.columns):,}")
    c3.metric("Numeric variables", f"{len(numeric.columns):,}")
    c4.metric("Missing cells", f"{missing:,}")

    st.subheader("🔬 Evidence summary")
    if numeric.empty:
        st.info("No numeric variables were detected. Upload experimental measurements for quantitative interpretation.")
    else:
        summary = numeric.describe().T
        summary["CV_%"] = numeric.std() / numeric.mean().replace(0, np.nan) * 100
        summary["Missing"] = numeric.isna().sum()
        summary = summary.reset_index().rename(columns={"index": "Variable"})
        st.dataframe(summary.round(5), width="stretch", hide_index=True)

        st.markdown("### Automatic observations")
        observations = []
        for _, row in summary.iterrows():
            name = str(row["Variable"])
            mean = row["mean"]
            sd = row["std"]
            minimum = row["min"]
            maximum = row["max"]
            if pd.notna(mean):
                observations.append(f"**{name}**: mean={mean:.5g}, SD={sd:.5g}, range={minimum:.5g}–{maximum:.5g}.")
        for text in observations[:20]:
            st.markdown("- " + text)

        st.download_button("⬇️ Download evidence summary", summary.to_csv(index=False).encode("utf-8"), "scimantra_ai_evidence_summary.csv", "text/csv")

st.divider()
st.subheader("🧠 Ask the research assistant")
question = st.text_area("Research question", placeholder="Example: What are the main trends in my treatment groups, and what should I check statistically?")

api_key = None
try:
    api_key = st.secrets.get("OPENAI_API_KEY")
except Exception:
    api_key = None

if api_key:
    st.success("AI provider configured securely through Streamlit Secrets.")
else:
    st.info("AI API is not configured yet. The evidence-summary mode above works without an API. Add OPENAI_API_KEY through Streamlit Secrets when you want model-generated interpretation. Never commit an API key to GitHub.")

if st.button("Generate research guidance", type="primary"):
    if not question.strip():
        st.warning("Enter a research question first.")
    elif _df is None:
        st.warning("Upload a dataset first so the assistant can ground its response in your data.")
    else:
        numeric = _df.select_dtypes(include="number")
        evidence = {"rows": int(len(_df)), "columns": list(map(str, _df.columns)), "missing_cells": int(_df.isna().sum().sum()), "numeric_summary": numeric.describe().round(6).to_dict() if not numeric.empty else {}}
        prompt = f"""You are a cautious scientific research assistant. Answer the user's research question using only the supplied dataset summary. Clearly separate calculated evidence from interpretation. Do not invent experiments, p-values, citations, biological mechanisms, or causal claims. Recommend appropriate statistical checks when needed. Mention uncertainty and limitations.\n\nQuestion: {question}\n\nDataset evidence:\n{json.dumps(evidence, default=str)}"""

        if not api_key:
            st.warning("No AI API key is configured. Below is a deterministic research checklist based on the uploaded evidence.")
            st.markdown("### Recommended next checks")
            checks = ["Confirm the experimental unit and replicate structure before selecting a statistical test.", "Inspect distributions and outliers rather than relying only on means.", "For treatment comparisons, choose the test based on the number of groups, pairing, and assumptions.", "Report effect sizes and uncertainty alongside p-values where appropriate.", "Do not infer causation from correlation or from an observational dataset alone.", "Document missing values, exclusions, transformations and preprocessing decisions."]
            for item in checks:
                st.markdown("- " + item)
        else:
            try:
                payload = json.dumps({"model": "gpt-4o-mini", "messages": [{"role": "system", "content": "You are an evidence-first scientific research assistant."}, {"role": "user", "content": prompt}], "temperature": 0.2}).encode("utf-8")
                req = urllib.request.Request("https://api.openai.com/v1/chat/completions", data=payload, headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}, method="POST")
                with urllib.request.urlopen(req, timeout=60) as response:
                    result = json.loads(response.read().decode("utf-8"))
                answer = result["choices"][0]["message"]["content"]
                st.markdown("### AI-assisted interpretation")
                st.markdown(answer)
                st.caption(f"Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}. Verify all scientific interpretations before publication.")
            except Exception as exc:
                st.error(f"AI request failed: {exc}")

st.divider()
st.caption("Scientific safeguard: this tool is an assistant, not a substitute for statistical review, domain expertise, peer review, or journal requirements. API credentials should be stored outside source code using Streamlit Secrets.")
