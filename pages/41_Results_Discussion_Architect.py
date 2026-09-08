import streamlit as st
import pandas as pd
from src.scimantra.results_discussion import result_statements, discussion_prompts, claim_levels

st.set_page_config(page_title="Results & Discussion Architect | SciMantra", page_icon="🧠", layout="wide")
st.title("🧠 Results → Discussion Architect")
st.caption("Separate what your data directly shows from what your scientific interpretation still needs to establish.")

comparison = st.session_state.get("last_comparison", {"status": "NO_DATA"})
hypothesis = st.text_input("Pre-specified hypothesis (optional)")

st.subheader("1. Results language")
for item in result_statements(comparison):
    st.write("• " + item)

st.subheader("2. Discussion architecture")
for prompt in discussion_prompts(comparison, hypothesis):
    st.write("• " + prompt)

st.subheader("3. Claim-strength ladder")
st.dataframe(pd.DataFrame(claim_levels()), use_container_width=True, hide_index=True)

st.info("Evidence rule: an observed difference is not automatically a statistically significant result, a mechanism, a causal effect, or a generalizable finding. Each stronger claim requires corresponding evidence and assumptions.")

st.subheader("4. Researcher evidence notes")
for label in ["Literature support", "Contradictory literature", "Alternative explanation", "Limitation", "Follow-up experiment"]:
    st.text_area(label, key="discussion_" + label.lower().replace(" ", "_"), height=80)

st.success("The architect is deliberately conservative: it structures scientific reasoning without manufacturing a narrative around unsupported results.")
