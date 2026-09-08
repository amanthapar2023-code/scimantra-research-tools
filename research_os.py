"""SciMantra Research OS — stable launchable research command center."""
import streamlit as st

st.set_page_config(page_title="SciMantra Research OS", page_icon="🔬", layout="wide", initial_sidebar_state="expanded")

STAGES = [
    ("01", "Research Question", "Define the problem, scope and question", "❓", "56_Research_Question_Hypothesis_Forge"),
    ("02", "Literature", "Retrieve and map evidence", "📚", "52_Literature_Evidence_Retriever"),
    ("03", "Hypothesis", "Create falsifiable hypotheses", "💡", "56_Research_Question_Hypothesis_Forge"),
    ("04", "Experiment", "Design experiments and controls", "🧪", "57_Research_Experiment_Architect"),
    ("05", "Data", "Extract and organize evidence", "🗃️", "53_Evidence_Extraction_Engine"),
    ("06", "Analysis", "Audit assumptions and robustness", "📊", "64_Statistical_Assumption_Audit"),
    ("07", "Evidence", "Synthesize evidence and gaps", "🔗", "54_Evidence_Synthesis_Gap_Engine"),
    ("08", "Claims", "Stress-test scientific claims", "🛡️", "69_Research_Claim_Stress_Test"),
    ("09", "Manuscript", "Build evidence-grounded writing", "📝", "49_Research_Manuscript_Studio"),
    ("10", "Peer Review", "Challenge the study before submission", "🧐", "74_Hostile_Peer_Review_Simulator"),
    ("11", "Submission", "Assess readiness and decision risks", "📤", "75_Research_Decision_Orchestrator"),
    ("12", "Next Study", "Turn findings into the next research cycle", "🔄", "75_Research_Decision_Orchestrator"),
]

if "os_project" not in st.session_state: st.session_state.os_project = "My Research Project"
if "os_question" not in st.session_state: st.session_state.os_question = ""
if "os_status" not in st.session_state: st.session_state.os_status = {name: "Not started" for _, name, _, _, _ in STAGES}

st.markdown("""
<style>
.block-container{max-width:1500px;padding-top:1.3rem}.hero{padding:2.2rem 2.4rem;border-radius:24px;border:1px solid #d7e6ef;background:linear-gradient(135deg,#eaf6ff,#ffffff,#eefaf4);margin-bottom:1.2rem}.hero .eyebrow{font-size:.78rem;font-weight:800;letter-spacing:.13em;text-transform:uppercase;color:#2574a8}.hero h1{font-size:2.75rem;margin:.25rem 0;color:#102b40}.hero p{font-size:1.08rem;color:#526b7b;max-width:980px}.card{border:1px solid #dce6ec;border-radius:16px;padding:1rem;background:#fff;min-height:145px;box-shadow:0 3px 14px rgba(20,55,80,.04)}.card h3{margin:.2rem 0;color:#17364b;font-size:1.05rem}.card p{color:#637785;font-size:.87rem;line-height:1.4}.launch{border:1px solid #dce6ec;border-radius:14px;padding:1rem;background:#fbfdff;margin:.5rem 0}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("🔬 SciMantra")
    st.caption("Research Operating System")
    st.divider()
    st.session_state.os_project = st.text_input("Project name", st.session_state.os_project)
    st.session_state.os_question = st.text_area("Central research question", st.session_state.os_question, placeholder="What are you trying to discover?")
    st.divider()
    st.success("Start with Research Forge. No special navigation API is required on this launch page.")

st.markdown("<div class='hero'><div class='eyebrow'>Integrated scientific workflow</div><h1>🔬 SciMantra Research OS</h1><p><b>From research idea to evidence, manuscript, peer-review challenge and the next study.</b><br>Use the links below to enter each specialist workbench.</p></div>", unsafe_allow_html=True)

# Plain internal links are deliberately used here instead of st.switch_page().
# This keeps the root launch page robust across Streamlit Community Cloud versions.
st.subheader("🚀 Start here")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("<div class='launch'><h3>❓ Research Forge</h3><p>Turn a research gap into precise questions and falsifiable hypotheses.</p></div>", unsafe_allow_html=True)
    st.markdown("[**Open Research Forge →**](./56_Research_Question_Hypothesis_Forge)")
with col2:
    st.markdown("<div class='launch'><h3>📚 Literature Intelligence</h3><p>Retrieve and organize literature evidence for the research problem.</p></div>", unsafe_allow_html=True)
    st.markdown("[**Open Literature Intelligence →**](./52_Literature_Evidence_Retriever)")
with col3:
    st.markdown("<div class='launch'><h3>🗂️ Project Workspace</h3><p>Organize the complete research lifecycle and its outputs.</p></div>", unsafe_allow_html=True)
    st.markdown("[**Open Project Workspace →**](./76_Unified_Research_Project_Workspace)")

complete = sum(v == "Complete" for v in st.session_state.os_status.values())
ready = sum(v == "Ready" for v in st.session_state.os_status.values())
blocked = sum(v == "Blocked" for v in st.session_state.os_status.values())
progress = round(100 * complete / len(STAGES))
m1,m2,m3,m4 = st.columns(4)
m1.metric("Project completion", f"{progress}%"); m2.metric("Complete", complete); m3.metric("Ready", ready); m4.metric("Blocked", blocked)
st.progress(progress / 100)

st.subheader("Research lifecycle")
cols = st.columns(4)
for i,(num,name,desc,icon,slug) in enumerate(STAGES):
    with cols[i % 4]:
        status = st.session_state.os_status[name]
        st.markdown(f"<div class='card'><small><b>{num} · {status.upper()}</b></small><h3>{icon} {name}</h3><p>{desc}</p></div>", unsafe_allow_html=True)
        new_status = st.selectbox("Status", ["Not started","In progress","Blocked","Ready","Complete"], index=["Not started","In progress","Blocked","Ready","Complete"].index(status), key=f"os_status_{num}", label_visibility="collapsed")
        st.session_state.os_status[name] = new_status
        st.markdown(f"[Open {name} →](./{slug})")

st.divider()
st.subheader("🛡️ Research OS control layer")
controls=[("🔗 Evidence provenance","Trace claims to results, analyses, datasets and source evidence."),("🛡️ Scientific integrity","Find contradictions, unsupported claims and verification gaps."),("🧪 Design quality","Audit controls, confounding, bias, assumptions and robustness."),("🧐 Reviewer readiness","Surface likely reviewer attacks before submission.")]
cols=st.columns(4)
for i,(title,desc) in enumerate(controls):
    with cols[i]: st.markdown(f"<div class='card'><h3>{title}</h3><p>{desc}</p></div>",unsafe_allow_html=True)

st.divider()
st.subheader("Connected intelligence chain")
st.markdown("**Literature → Evidence Matrix → Novelty → Research Gap → Research Forge → Experiment → Design Optimization → Pilot → Falsification → Causal/Bias Audit → Statistics → Robustness → Reproducibility → Provenance → Integrity → Claim Stress Test → Evidence Sufficiency → Generalizability → Mechanism → Prior Art → Peer Review → Decision → Next Study**")
st.success("Research OS launch page is active. Begin with **Research Forge**.")
st.caption("Decision support only. SciMantra does not certify scientific validity, novelty, causality, or publication acceptance.")
