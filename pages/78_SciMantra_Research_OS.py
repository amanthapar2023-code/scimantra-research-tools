"""SciMantra Research OS — integrated command center for the research workflow."""
import streamlit as st
from datetime import datetime

STAGES = [
    ("01", "Research Question", "Define the problem, question and scope", "🎯", "pages/56_Research_Question_Hypothesis_Forge.py"),
    ("02", "Literature", "Map evidence, methods and research gaps", "📚", "pages/52_Literature_Evidence_Retriever.py"),
    ("03", "Hypothesis", "Forge testable hypotheses and predictions", "💡", "pages/56_Research_Question_Hypothesis_Forge.py"),
    ("04", "Experiment", "Design experiments, controls and power", "🧪", "pages/57_Research_Experiment_Architect.py"),
    ("05", "Data", "Capture datasets, provenance and quality", "🗃️", "pages/53_Evidence_Extraction_Engine.py"),
    ("06", "Analysis", "Choose, audit and stress-test analyses", "📊", "pages/64_Statistical_Assumption_Audit.py"),
    ("07", "Evidence", "Synthesize evidence and contradictions", "🔗", "pages/54_Evidence_Synthesis_Gap_Engine.py"),
    ("08", "Claims", "Stress-test scope, support and novelty", "🛡️", "pages/69_Research_Claim_Stress_Test.py"),
    ("09", "Manuscript", "Build evidence-grounded scientific writing", "📝", "pages/49_Research_Manuscript_Studio.py"),
    ("10", "Peer Review", "Attack weaknesses and manage responses", "🧐", "pages/74_Hostile_Peer_Review_Simulator.py"),
    ("11", "Submission", "Audit journal requirements and readiness", "📤", "pages/75_Research_Decision_Orchestrator.py"),
    ("12", "Next Study", "Turn findings into the next research cycle", "🔄", "pages/75_Research_Decision_Orchestrator.py"),
]
STATUS = ["Not started", "In progress", "Blocked", "Ready", "Complete"]

st.set_page_config(page_title="SciMantra Research OS", page_icon="🔬", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
.block-container{max-width:1500px;padding-top:1.5rem}.os-hero{padding:2.1rem 2.3rem;border-radius:24px;border:1px solid #dce7ef;background:linear-gradient(135deg,#edf7ff,#fff,#eefaf4);margin-bottom:1.2rem}.eyebrow{font-size:.78rem;font-weight:800;letter-spacing:.13em;text-transform:uppercase;color:#2474a7}.os-hero h1{font-size:2.7rem;margin:.2rem 0;color:#102b40}.os-hero p{font-size:1.08rem;color:#536a7a;margin:0;max-width:900px}.stage{border:1px solid #dce6ec;border-radius:17px;padding:1rem;background:#fff;min-height:145px;box-shadow:0 3px 14px rgba(20,55,80,.04)}.stage .num{font-size:.75rem;font-weight:800;color:#6d8493}.stage h3{font-size:1.03rem;margin:.25rem 0;color:#17364b}.stage p{font-size:.85rem;color:#637785;line-height:1.4}.signal{border:1px solid #dce6ec;border-radius:14px;padding:.9rem 1rem;background:#fff}.signal b{display:block;color:#18384c}.signal span{font-size:.83rem;color:#687d8b}.tool{border:1px solid #dce6ec;border-radius:12px;padding:.8rem 1rem;background:#fbfdff;margin:.4rem 0}
</style>
""", unsafe_allow_html=True)

if "os_project" not in st.session_state: st.session_state.os_project = "My Research Project"
if "os_question" not in st.session_state: st.session_state.os_question = ""
if "os_status" not in st.session_state: st.session_state.os_status = {s[1]: "Not started" for s in STAGES}

st.markdown('<div class="os-hero"><div class="eyebrow">Integrated research operating system</div><h1>🔬 SciMantra Research OS</h1><p>One workspace connecting your research question, literature, experiment, data, analysis, evidence, claims, manuscript and submission readiness.</p></div>', unsafe_allow_html=True)
with st.sidebar:
    st.header("Project")
    st.session_state.os_project = st.text_input("Project name", st.session_state.os_project)
    st.session_state.os_question = st.text_area("Central research question", st.session_state.os_question, placeholder="What exactly are you trying to discover?")
    st.divider()
    st.caption("Stage cards point to specialist workbenches. Project artifacts can now be managed centrally.")

complete = sum(v == "Complete" for v in st.session_state.os_status.values()); ready = sum(v == "Ready" for v in st.session_state.os_status.values()); blocked = sum(v == "Blocked" for v in st.session_state.os_status.values()); progress = round(100 * complete / len(STAGES))
a,b,c,d = st.columns(4); a.metric("Project completion", f"{progress}%"); b.metric("Complete", complete); c.metric("Ready next", ready); d.metric("Blocked", blocked)
st.progress(progress / 100)

st.subheader("🚀 Project command center")
c1,c2,c3,c4 = st.columns(4)
with c1:
    st.markdown("**🗂️ Artifact Manager**")
    st.caption("Register, search, review and archive datasets, figures, tables, claims, protocols and manuscripts.")
    st.markdown("[Open Project Artifact Manager →](./80_Project_Artifact_Manager)")
with c2:
    st.markdown("**🔗 Cross-Tool Linkage**")
    st.caption("Connect outputs across the research lifecycle and trace upstream/downstream dependencies.")
    st.markdown("[Open Cross-Tool Linkage →](./79_Cross_Tool_Data_Linkage)")
with c3:
    st.markdown("**🗂️ Unified Workspace**")
    st.caption("Track the complete project lifecycle and its current research state.")
    st.markdown("[Open Unified Workspace →](./76_Unified_Research_Project_Workspace)")
with c4:
    st.markdown("**☁️ Persistent State & Sync**")
    st.caption("Load and save Research OS state using authenticated, project-scoped cloud snapshots with conflict protection.")
    st.markdown("[Open Persistent State & Sync →](./115_Research_OS_Persistent_State)")

st.subheader("Research lifecycle")
cols = st.columns(4)
for i, (num,name,desc,icon,path) in enumerate(STAGES):
    with cols[i % 4]:
        current = st.session_state.os_status[name]
        st.markdown(f'<div class="stage"><div class="num">{num} · {current.upper()}</div><h3>{icon} {name}</h3><p>{desc}</p></div>', unsafe_allow_html=True)
        new = st.selectbox("Status", STATUS, index=STATUS.index(current), key=f"status_{num}", label_visibility="collapsed")
        st.session_state.os_status[name] = new
        st.caption(f"Workbench: `{path.split('/')[-1]}`")

st.divider(); st.subheader("Connected specialist workbenches")
for num,name,desc,icon,path in STAGES:
    st.markdown(f'<div class="tool"><b>{icon} {name}</b> &nbsp;→&nbsp; <code>{path}</code></div>', unsafe_allow_html=True)

st.divider(); st.subheader("Research OS control layer")
signals=[("🔗 Evidence provenance","Trace claims back to results, analyses, datasets and raw evidence."),("🛡️ Scientific integrity","Check contradictions, unsupported claims and verification gaps."),("🧪 Design quality","Audit controls, confounding, bias, assumptions and robustness."),("🧐 Reviewer readiness","Surface likely reviewer attacks before submission.")]
cols=st.columns(4)
for i,(title,desc) in enumerate(signals):
    with cols[i]: st.markdown(f'<div class="signal"><b>{title}</b><span>{desc}</span></div>', unsafe_allow_html=True)

st.subheader("Next actions")
actions=[]
for name in [x[1] for x in STAGES]:
    s=st.session_state.os_status[name]
    if s in {"Blocked","In progress","Not started"}: actions.append(("🔴" if s=="Blocked" else "🟡",name,s))
if actions:
    for icon,name,s in actions[:8]: st.write(f"{icon} **{name}** — {s}")
else: st.success("All lifecycle stages are marked complete. Move to the next research cycle.")

st.subheader("Current SciMantra intelligence chain")
st.info("Literature → evidence matrix → novelty → gap → question/hypothesis → experiment → design optimization → synthetic pilot → falsification → causal/confounding audit → bias/error → statistical assumptions → robustness → reproducibility → provenance → contradiction/integrity → claim stress test → evidence sufficiency → generalizability → mechanism consistency → prior-art challenge → hostile peer review → decision orchestration → unified workspace → cross-tool linkage → artifact management → Research OS → persistent state & cloud synchronization.")
st.caption(f"Workspace snapshot: {datetime.now().strftime('%Y-%m-%d %H:%M')} · Decision support only; scientific validity remains the researcher's responsibility.")
