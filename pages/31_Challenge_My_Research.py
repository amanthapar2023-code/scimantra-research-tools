import re
import streamlit as st

st.set_page_config(page_title="Challenge My Research | SciMantra", page_icon="🔥", layout="wide")
st.title("🔥 Challenge My Research")
st.caption("A pre-submission scientific stress test — attack the reasoning before a reviewer does.")
st.warning("This is a critical-thinking simulator, not a peer review and not proof that a study is valid.")

project = st.session_state.get("ri_title", "")
title = st.text_input("Research title", value=project, key="challenge_title")
abstract = st.text_area("Paste your abstract / study summary", height=220, placeholder="Include your objective, methods, main findings and conclusion. Do not invent findings for this test.")
conclusion = st.text_area("Main conclusion", height=120, placeholder="What do you believe your study demonstrates?")

if st.button("🔥 ATTACK MY RESEARCH", type="primary", use_container_width=True):
    text = " ".join([title, abstract, conclusion]).strip()
    if not text:
        st.error("Enter at least a title or study summary.")
        st.stop()

    checks = []
    low = text.lower()
    def add(severity, area, finding, action):
        checks.append((severity, area, finding, action))

    if not re.search(r"\b(control|untreated|blank|baseline|reference|benchmark)\b", low):
        add("HIGH", "Controls", "No explicit control/benchmark was detected in the supplied text.", "State the comparator and explain why it is scientifically appropriate.")
    if not re.search(r"\b(replicat|n\s*=|biological replicat|technical replicat)\w*", low):
        add("HIGH", "Replication", "Replication is not explicit.", "Report independent experimental units and justify the replicate structure.")
    if not re.search(r"\b(p\s*[<=>]|confidence interval|95%|effect size|anova|t[- ]test|regression|mann[- ]whitney|kruskal|mixed[- ]effects)\b", low):
        add("MEDIUM", "Statistics", "No statistical method or uncertainty measure was detected.", "Pre-specify the analysis and report effect size/uncertainty where appropriate.")
    if re.search(r"\b(prove|proves|proven|definitively|always|never|first ever|no studies|all studies)\b", low):
        add("HIGH", "Claim strength", "Absolute language was detected.", "Replace absolute wording unless exhaustive evidence genuinely supports it.")
    if not re.search(r"\b(limit|limitation|caveat|uncertain|uncertainty)\w*", low):
        add("MEDIUM", "Limitations", "No limitations or uncertainty are visible.", "State important limitations and distinguish what was measured from what was inferred.")
    if not re.search(r"\b(mechanis|cause|causal|alternative|confound|control)\w*", low):
        add("MEDIUM", "Causality", "The summary does not show how alternative explanations were tested.", "Identify plausible competing explanations and the experiment/analysis that distinguishes them.")
    if not re.search(r"\b(data|dataset|raw|measurement|sample|specimen)\w*", low):
        add("LOW", "Traceability", "The evidence/data layer is not explicit.", "Link conclusions to measurable observations and retain raw-data provenance.")

    if not checks:
        add("LOW", "General", "No obvious red flags were detected by this rule-based screen.", "Run the full evidence, statistics and reviewer engines before submission.")

    score = max(0, 100 - sum(18 if s == "HIGH" else 9 if s == "MEDIUM" else 3 for s, *_ in checks))
    st.subheader("Publication-readiness stress score")
    st.metric("Initial stress-test score", f"{score}/100")
    st.caption("This score is heuristic. It is intentionally conservative and should never be presented as a probability of acceptance.")

    tabs = st.tabs(["🧑‍⚖️ Reviewer 1 — Methodology", "📊 Reviewer 2 — Statistics", "🧠 Reviewer 3 — Novelty", "⚔️ Skeptical Reviewer", "🛠️ Fix Priority"])
    for tab, focus in zip(tabs, ["Methodology", "Statistics", "Novelty", "Skeptical review", "Fix priority"]):
        with tab:
            subset = checks
            if focus == "Statistics": subset = [x for x in checks if x[1] in ["Statistics", "Replication", "Causality"]]
            elif focus == "Methodology": subset = [x for x in checks if x[1] in ["Controls", "Replication", "Traceability", "Limitations"]]
            elif focus == "Novelty": subset = [x for x in checks if x[1] in ["Novelty", "Claim strength"]]
            elif focus == "Skeptical review": subset = sorted(checks, key=lambda x: {"HIGH":0,"MEDIUM":1,"LOW":2}[x[0]])
            for sev, area, finding, action in subset:
                icon = "🔴" if sev == "HIGH" else "🟠" if sev == "MEDIUM" else "🟢"
                st.markdown(f"### {icon} {sev} — {area}")
                st.write(f"**Challenge:** {finding}")
                st.write(f"**Recommended response:** {action}")

    st.subheader("🧨 Questions a hostile reviewer may ask")
    questions = [
        "What is the strongest alternative explanation for your main finding?",
        "What control would make your conclusion substantially weaker if it failed?",
        "Are your replicates independent experimental units or repeated measurements of the same unit?",
        "Does statistical significance correspond to a scientifically meaningful effect?",
        "Which statement in the manuscript is stronger than the evidence actually permits?",
        "What result would falsify your preferred explanation?",
        "Could another laboratory reproduce the study from your Methods section alone?",
        "What exactly is novel compared with the closest existing study?",
    ]
    for q in questions: st.checkbox(q, key="q_" + str(abs(hash(q))))

st.divider()
st.success("Next engine: connect this stress test to the Research Genome, evidence matrix and uploaded experimental data so every reviewer challenge can point to a specific claim, experiment, table or figure.")
