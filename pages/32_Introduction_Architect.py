import streamlit as st
import pandas as pd
from src.scimantra.research_intelligence import generate_blueprint, crossref_search

st.set_page_config(page_title="Introduction Architect | SciMantra", page_icon="✍️", layout="wide")
st.title("✍️ Introduction Architect")
st.caption("Turn your literature into an evidence-aware Introduction plan — without inventing citations or results.")

title = st.text_input("Research title", key="ia_title", placeholder="Enter your research title")
if st.button("Build Introduction Architecture", type="primary") and title.strip():
    st.session_state.ia_bp = generate_blueprint(title.strip())
    try:
        st.session_state.ia_papers = crossref_search(title.strip(), rows=10)
    except Exception:
        st.session_state.ia_papers = []

if "ia_bp" not in st.session_state:
    st.info("Enter a title to generate the architecture.")
    st.stop()

bp = st.session_state.ia_bp
papers = st.session_state.get("ia_papers", [])

st.subheader("The 9-block Introduction Matrix")
blocks = [
    ("1. Problem", "What important scientific/technical problem exists?", bp["components"].get("Problem / system", "")),
    ("2. Challenges", "What prevents the problem from being solved adequately?", "Extract limitations, bottlenecks and unresolved mechanisms from the literature."),
    ("3. What previous research did", "What solutions have already been attempted?", "Map each anchor paper to its intervention, method and outcome."),
    ("4. Technology / approach", "Which technologies or approaches dominate the field?", bp["components"].get("Technology / approach", "")),
    ("5. Innovation", "What could your study add that is testable?", "Generate candidate novelty only after checking the evidence matrix."),
    ("6. Difference", "How is your proposed study distinguishable?", "Compare system, variables, controls, method, dataset and endpoint—not wording alone."),
    ("7. Research gap", "What remains unanswered?", bp["gap"][0] if bp["gap"] else "Candidate gap requires literature verification."),
    ("8. Method", "How will the gap be tested?", bp["method"][0] if bp["method"] else "Define design, controls, replication and primary endpoint."),
    ("9. Results → Discussion", "What evidence will answer the question?", "Predefine outcome metrics and competing explanations; never fabricate results."),
]
rows=[]
for name, question, guidance in blocks:
    with st.expander(name, expanded=True):
        st.markdown(f"**Writing question:** {question}")
        st.write(guidance)
        draft=st.text_area("Your notes / evidence", key="ia_"+name)
        rows.append({"Block":name,"Writing question":question,"Your notes":draft})

st.divider()
st.subheader("📚 Anchor-paper workspace")
if papers:
    df=pd.DataFrame([{"Year":p.get("Year"),"Journal":p.get("Journal"),"Title":p.get("Title"),"DOI":p.get("DOI")} for p in papers])
    st.dataframe(df,width="stretch",hide_index=True)
else:
    st.caption("No literature metadata was retrieved. Add verified papers manually in your next iteration.")

st.download_button("⬇️ Export Introduction Matrix", pd.DataFrame(rows).to_csv(index=False).encode(), "scimantra_introduction_matrix.csv", "text/csv")
st.warning("Citation rule: use the matrix to organize verified evidence. Do not convert generated statements into factual claims until supported by the underlying paper.")
