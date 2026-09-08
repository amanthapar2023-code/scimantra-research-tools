import pandas as pd
import streamlit as st

from src.scimantra.research_intelligence import (
    build_matrix,
    crossref_search,
    generate_blueprint,
    novelty_report,
)

st.set_page_config(page_title="Research Intelligence | SciMantra", page_icon="🧠", layout="wide")

st.markdown("""
<style>
.hero-ri{padding:2rem 2.2rem;border-radius:22px;background:linear-gradient(135deg,#eef7ff,#ffffff 55%,#f3fff8);border:1px solid #d8e8f5;margin-bottom:1.2rem}
.hero-ri h1{margin:0;color:#102b40;font-size:2.35rem}.hero-ri p{color:#526a7b;font-size:1.05rem;margin:.45rem 0 0}
.card{border:1px solid #dfe8ee;border-radius:16px;padding:1rem;background:white;height:100%}.card h3{margin:.1rem 0 .4rem;color:#18364b}.muted{color:#637889}
.badge{display:inline-block;padding:.35rem .7rem;border-radius:999px;background:#edf6ff;border:1px solid #cfe4f5;font-weight:700;color:#23658d}
</style>
<div class="hero-ri">
<div class="badge">🧠 RESEARCH INTELLIGENCE ENGINE · V0.1</div>
<h1>From Research Title → Research Blueprint</h1>
<p>Build an evidence-aware starting point for a research project. SciMantra generates hypotheses and research directions, then separates them from verified literature evidence.</p>
</div>
""", unsafe_allow_html=True)

with st.form("research_title_form"):
    title = st.text_input("Enter your research title", placeholder="e.g., Biological removal of H₂S from industrial wastewater using sulfur-oxidizing bacteria")
    c1, c2 = st.columns([3, 1])
    with c1:
        st.caption("Start with only the title. You can refine the field and assumptions after the first blueprint.")
    with c2:
        submitted = st.form_submit_button("🚀 Build Research Intelligence", type="primary", use_container_width=True)

if submitted:
    if not title.strip():
        st.warning("Enter a research title first.")
        st.stop()
    st.session_state["ri_title"] = title.strip()
    with st.spinner("Deconstructing the research idea…"):
        st.session_state["ri_blueprint"] = generate_blueprint(title.strip())
    with st.spinner("Searching Crossref for initial literature signals…"):
        try:
            st.session_state["ri_papers"] = crossref_search(title.strip(), rows=15)
            st.session_state["ri_search_error"] = ""
        except Exception as exc:
            st.session_state["ri_papers"] = []
            st.session_state["ri_search_error"] = str(exc)

if "ri_blueprint" not in st.session_state:
    st.info("👆 Enter a research title above to create your first Research Genome snapshot.")
    st.markdown("### What this first version does")
    cols = st.columns(4)
    for col, (h, d) in zip(cols, [
        ("🧬 Deconstruct", "Break the title into problem, approach, target, outcome and context."),
        ("🕳️ Find gaps", "Turn vague 'research gaps' into testable questions and evidence gaps."),
        ("💥 Check collisions", "Compare the title with retrieved literature and flag close matches."),
        ("🧪 Plan the study", "Suggest controls, replication, outcomes and competing explanations."),
    ]):
        with col:
            st.markdown(f'<div class="card"><h3>{h}</h3><div class="muted">{d}</div></div>', unsafe_allow_html=True)
    st.stop()

bp = st.session_state["ri_blueprint"]
papers = st.session_state.get("ri_papers", [])

st.subheader("🧬 Research Genome")
components = bp["components"]
cols = st.columns(5)
for col, (k, v) in zip(cols, components.items()):
    with col:
        st.markdown(f"**{k}**")
        st.write(v)

st.divider()
tabs = st.tabs(["🕳️ Research Gaps", "❓ Questions", "🎯 Objectives", "🧠 Hypotheses", "🧪 Study Design", "📚 Evidence Matrix", "💥 Novelty Collision"])

with tabs[0]:
    st.markdown("### Candidate research gaps")
    st.caption("These are candidate directions generated from the title, not claims that the literature has already proven a gap.")
    for i, item in enumerate(bp["gap"], 1):
        st.markdown(f"**Gap {i}.** {item}")

with tabs[1]:
    for i, q in enumerate(bp["questions"], 1):
        st.markdown(f"**RQ{i}.** {q}")

with tabs[2]:
    for i, obj in enumerate(bp["objectives"], 1):
        st.markdown(f"**O{i}.** {obj}")

with tabs[3]:
    st.markdown("### Candidate hypotheses")
    for h in bp["hypotheses"]:
        st.markdown(f"- {h}")
    st.warning("Hypotheses are proposed starting points. Validate them against your field, protocol and prior evidence before using them in a manuscript.")

with tabs[4]:
    st.markdown("### Pre-experiment design checklist")
    for item in bp["method"]:
        st.checkbox(item, value=False, key="ri_" + str(abs(hash(item))))
    st.markdown("### Next-generation checks planned")
    st.write("Missing-control detection • confounder analysis • alternative-hypothesis testing • power/sample-size planning • statistical-assumption checks")

with tabs[5]:
    if st.session_state.get("ri_search_error"):
        st.warning("The literature metadata service could not be reached right now. The title blueprint is still available.")
    if papers:
        matrix = build_matrix(papers, st.session_state["ri_title"])
        st.dataframe(pd.DataFrame(matrix), use_container_width=True, hide_index=True)
        st.caption("Initial matrix uses bibliographic metadata. Claim-level extraction will require abstracts/full text in a later engine version.")
    else:
        st.info("No literature metadata was retrieved yet. Try the title again when the literature service is available.")

with tabs[6]:
    report = novelty_report(st.session_state["ri_title"], papers)
    st.markdown(f"## {report['level']}")
    st.write(report["explanation"])
    if report["high"]:
        st.markdown("### Closest title-level matches")
        for p in report["high"]:
            st.write(f"• **{p['Title']}** — {p.get('Year','')} — {p.get('DOI','')}")
    if report["medium"]:
        st.markdown("### Related matches")
        for p in report["medium"]:
            st.write(f"• **{p['Title']}** — {p.get('Year','')} — {p.get('DOI','')}")
    st.info("A low collision score is not proof of scientific novelty. A proper novelty assessment must inspect concepts, methods, datasets, claims and citation networks.")

st.divider()
st.markdown("### 🔒 Scientific integrity rule")
st.success("SciMantra does not invent experimental results. Until actual data and verified sources are provided, generated content is explicitly treated as a research hypothesis, planning aid, or candidate interpretation.")
