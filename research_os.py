"""SciMantra Research OS — launchable research command center.

This file is intentionally a root-level Streamlit entrypoint so Community Cloud can
launch the Research OS directly while the existing app.py remains available.
"""
import streamlit as st

st.set_page_config(
    page_title="SciMantra Research OS",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

STAGES = [
    ("01", "Research Question", "Define the problem, scope and question", "pages/56_Research_Question_Hypothesis_Forge.py"),
    ("02", "Literature", "Retrieve and map evidence", "pages/52_Literature_Evidence_Retriever.py"),
    ("03", "Hypothesis", "Create falsifiable hypotheses", "pages/56_Research_Question_Hypothesis_Forge.py"),
    ("04", "Experiment", "Design experiments and controls", "pages/57_Research_Experiment_Architect.py"),
    ("05", "Data", "Extract and organize evidence", "pages/53_Evidence_Extraction_Engine.py"),
    ("06", "Analysis", "Audit assumptions and robustness", "pages/64_Statistical_Assumption_Audit.py"),
    ("07", "Evidence", "Synthesize evidence and gaps", "pages/54_Evidence_Synthesis_Gap_Engine.py"),
    ("08", "Claims", "Stress-test scientific claims", "pages/69_Research_Claim_Stress_Test.py"),
    ("09", "Manuscript", "Build evidence-grounded writing", "pages/49_Research_Manuscript_Studio.py"),
    ("10", "Peer Review", "Challenge the study before submission", "pages/74_Hostile_Peer_Review_Simulator.py"),
    ("11", "Submission", "Assess readiness and decision risks", "pages/75_Research_Decision_Orchestrator.py"),
    ("12", "Next Study", "Turn findings into the next research cycle", "pages/75_Research_Decision_Orchestrator.py"),
]

if "os_project" not in st.session_state:
    st.session_state.os_project = "My Research Project"
if "os_question" not in st.session_state:
    st.session_state.os_question = ""
if "os_status" not in st.session_state:
    st.session_state.os_status = {name: "Not started" for _, name, _, _ in STAGES}

st.markdown("""
<style>
.block-container{max-width:1500px;padding-top:1.3rem}
.hero{padding:2.2rem 2.4rem;border-radius:24px;border:1px solid #d7e6ef;background:linear-gradient(135deg,#eaf6ff,#ffffff,#eefaf4);margin-bottom:1.2rem}
.hero .eyebrow{font-size:.78rem;font-weight:800;letter-spacing:.13em;text-transform:uppercase;color:#2574a8}
.hero h1{font-size:2.75rem;margin:.25rem 0;color:#102b40}.hero p{font-size:1.08rem;color:#526b7b;max-width:980px}
.card{border:1px solid #dce6ec;border-radius:16px;padding:1rem;background:#fff;min-height:145px;box-shadow:0 3px 14px rgba(20,55,80,.04)}
.card h3{margin:.2rem 0;color:#17364b;font-size:1.05rem}.card p{color:#637785;font-size:.87rem;line-height:1.4}
.flow{border:1px solid #dce6ec;border-radius:14px;padding:.9rem;background:#fbfdff;margin-bottom:.65rem}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("🔬 SciMantra")
    st.caption("Research Operating System")
    st.divider()
    st.session_state.os_project = st.text_input("Project name", st.session_state.os_project)
    st.session_state.os_question = st.text_area(
        "Central research question",
        st.session_state.os_question,
        placeholder="What are you trying to discover?",
    )
    st.divider()
    st.info("Start with Research Forge. The remaining stages open the existing SciMantra specialist workbenches.")

st.markdown("<div class='hero'><div class='eyebrow'>Integrated scientific workflow</div><h1>🔬 SciMantra Research OS</h1><p>From research idea to evidence, manuscript, peer-review challenge and the next study — one connected workspace.</p></div>", unsafe_allow_html=True)

# Primary launch actions.
a, b, c = st.columns([1.4, 1.4, 1])
with a:
    if st.button("🚀 Start Research Forge", type="primary", width="stretch"):
        st.switch_page("pages/56_Research_Question_Hypothesis_Forge.py")
with b:
    if st.button("📚 Open Literature Intelligence", width="stretch"):
        st.switch_page("pages/52_Literature_Evidence_Retriever.py")
with c:
    st.metric("Lifecycle stages", "12")

complete = sum(v == "Complete" for v in st.session_state.os_status.values())
ready = sum(v == "Ready" for v in st.session_state.os_status.values())
blocked = sum(v == "Blocked" for v in st.session_state.os_status.values())
progress = round(100 * complete / len(STAGES))

m1, m2, m3, m4 = st.columns(4)
m1.metric("Project completion", f"{progress}%")
m2.metric("Complete", complete)
m3.metric("Ready", ready)
m4.metric("Blocked", blocked)
st.progress(progress / 100)

st.subheader("Research lifecycle")
cols = st.columns(4)
for i, (num, name, desc, path) in enumerate(STAGES):
    with cols[i % 4]:
        status = st.session_state.os_status[name]
        st.markdown(
            f"<div class='card'><small><b>{num} · {status.upper()}</b></small><h3>{name}</h3><p>{desc}</p></div>",
            unsafe_allow_html=True,
        )
        new_status = st.selectbox(
            "Status",
            ["Not started", "In progress", "Blocked", "Ready", "Complete"],
            index=["Not started", "In progress", "Blocked", "Ready", "Complete"].index(status),
            key=f"os_status_{num}",
            label_visibility="collapsed",
        )
        st.session_state.os_status[name] = new_status
        if st.button(f"Open {name}", key=f"open_{num}", width="stretch"):
            st.switch_page(path)

st.divider()
st.subheader("Research Forge — the starting point")
st.write("Use **Research Question & Hypothesis Forge** to convert a verified/working research gap into precise questions and falsifiable hypothesis candidates. The specialist page is already part of this repository.")
if st.button("❓ Open Research Question & Hypothesis Forge", width="stretch"):
    st.switch_page("pages/56_Research_Question_Hypothesis_Forge.py")

st.divider()
st.subheader("Control layer")
controls = [
    ("🔗 Evidence provenance", "Trace claims to results, analyses, datasets and source evidence."),
    ("🛡️ Scientific integrity", "Find contradictions, unsupported claims and verification gaps."),
    ("🧪 Design quality", "Audit controls, confounding, bias, assumptions and robustness."),
    ("🧐 Reviewer readiness", "Surface likely reviewer attacks before submission."),
]
cols = st.columns(4)
for i, (title, desc) in enumerate(controls):
    with cols[i]:
        st.markdown(f"<div class='card'><h3>{title}</h3><p>{desc}</p></div>", unsafe_allow_html=True)

st.divider()
st.subheader("Connected intelligence chain")
st.markdown("**Literature → Evidence Matrix → Novelty → Research Gap → Research Forge → Experiment → Design Optimization → Pilot → Falsification → Causal/Bias Audit → Statistics → Robustness → Reproducibility → Provenance → Integrity → Claim Stress Test → Evidence Sufficiency → Generalizability → Mechanism → Prior Art → Peer Review → Decision → Next Study**")

st.success("Research OS is ready to use. Start with **Research Forge** if you are beginning a new project.")
st.caption("Decision support only. SciMantra does not certify scientific validity, novelty, causality, or publication acceptance.")
