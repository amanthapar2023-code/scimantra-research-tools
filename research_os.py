"""SciMantra Research OS — integrated research command center."""
import streamlit as st
import pandas as pd
from src.scimantra.research_os_state import STAGE_NAMES, STATUS_VALUES, add_artifact, from_json, new_project, progress, set_stage, to_json

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

if "os_project_data" not in st.session_state:
    st.session_state.os_project_data = new_project()
project = st.session_state.os_project_data

with st.sidebar:
    st.title("🔬 SciMantra")
    st.caption("Research Operating System")
    st.divider()
    project_name = st.text_input("Project name", project["project"]["name"])
    research_question = st.text_area("Central research question", project["project"]["question"], placeholder="What are you trying to discover?")
    if project_name != project["project"]["name"] or research_question != project["project"]["question"]:
        project["project"]["name"] = project_name.strip() or "My Research Project"
        project["project"]["question"] = research_question.strip()
        st.session_state.os_project_data = project
        st.session_state.os_project = project["project"]["name"]
        st.session_state.os_question = project["project"]["question"]
        st.session_state.ri_title = project["project"]["name"]
    st.divider()
    st.success("Project state is shared across this Streamlit session. Export it before ending the session to preserve the current project snapshot.")

st.markdown("""
<style>
.block-container{max-width:1500px;padding-top:1.3rem}.hero{padding:2.2rem 2.4rem;border-radius:24px;border:1px solid #d7e6ef;background:linear-gradient(135deg,#eaf6ff,#ffffff,#eefaf4);margin-bottom:1.2rem}.hero .eyebrow{font-size:.78rem;font-weight:800;letter-spacing:.13em;text-transform:uppercase;color:#2574a8}.hero h1{font-size:2.75rem;margin:.25rem 0;color:#102b40}.hero p{font-size:1.08rem;color:#526b7b;max-width:980px}.card{border:1px solid #dce6ec;border-radius:16px;padding:1rem;background:#fff;min-height:145px;box-shadow:0 3px 14px rgba(20,55,80,.04)}.card h3{margin:.2rem 0;color:#17364b;font-size:1.05rem}.card p{color:#637785;font-size:.87rem;line-height:1.4}.launch{border:1px solid #dce6ec;border-radius:14px;padding:1rem;background:#fbfdff;margin:.5rem 0}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='hero'><div class='eyebrow'>Integrated scientific workflow</div><h1>🔬 SciMantra Research OS</h1><p><b>From research idea to evidence, manuscript, peer-review challenge and the next study.</b><br>The OS carries a shared project state and artifact registry while you work across specialist pages.</p></div>", unsafe_allow_html=True)

st.subheader("🚀 Start here")
col1, col2, col3, col4 = st.columns(4)
for col, title, desc, link in [
    (col1, "❓ Research Forge", "Turn a research gap into precise questions and falsifiable hypotheses.", "./56_Research_Question_Hypothesis_Forge"),
    (col2, "📚 Literature Intelligence", "Retrieve and organize literature evidence for the research problem.", "./52_Literature_Evidence_Retriever"),
    (col3, "🗂️ Project Workspace", "Organize the research lifecycle, outputs and project state.", "./76_Unified_Research_Project_Workspace"),
    (col4, "🔗 Data Linkage", "Connect outputs from different tools into an explicit artifact graph.", "./79_Cross_Tool_Data_Linkage"),
]:
    with col:
        st.markdown(f"<div class='launch'><h3>{title}</h3><p>{desc}</p></div>", unsafe_allow_html=True)
        st.markdown(f"[**Open →**]({link})")

p = progress(project)
completion = round(100 * p["complete"] / p["total"])
m1,m2,m3,m4 = st.columns(4)
m1.metric("Project completion", f"{completion}%"); m2.metric("Complete", p["complete"]); m3.metric("In progress", p["in_progress"]); m4.metric("Blocked", p["blocked"])
st.progress(completion / 100)

st.subheader("Research lifecycle")
cols = st.columns(4)
for i,(num,name,desc,icon,slug) in enumerate(STAGES):
    with cols[i % 4]:
        status = project["stages"][name]["status"]
        st.markdown(f"<div class='card'><small><b>{num} · {status.upper()}</b></small><h3>{icon} {name}</h3><p>{desc}</p></div>", unsafe_allow_html=True)
        new_status = st.selectbox("Status", STATUS_VALUES, index=STATUS_VALUES.index(status), key=f"os_status_{num}", label_visibility="collapsed")
        if new_status != status:
            project = set_stage(project, name, status=new_status)
            st.session_state.os_project_data = project
        st.markdown(f"[Open {name} →](./{slug})")

st.divider(); st.subheader("🧩 Project data bus")
left, right = st.columns([1.15, 1])
with left:
    st.markdown("**Register an output from any research stage**")
    with st.form("artifact_form"):
        a1,a2 = st.columns(2)
        artifact_title = a1.text_input("Artifact title", placeholder="e.g., Literature evidence matrix")
        artifact_type = a2.selectbox("Artifact type", ["Question","Hypothesis","Literature","Dataset","Analysis","Result","Figure","Table","Claim","Protocol","Manuscript","Review","Other"])
        a3,a4 = st.columns(2)
        artifact_stage = a3.selectbox("Research stage", STAGE_NAMES)
        artifact_source = a4.text_input("Source / file / DOI", placeholder="Optional provenance anchor")
        artifact_description = st.text_area("Description", placeholder="What does this artifact contain or establish?")
        submitted = st.form_submit_button("➕ Add to project", type="primary")
    if submitted:
        try:
            project = add_artifact(project, artifact_title, artifact_type, artifact_stage, artifact_source, artifact_description)
            st.session_state.os_project_data = project
            st.success(f"Added **{artifact_title.strip()}** to {artifact_stage}.")
        except ValueError as exc: st.error(str(exc))
with right:
    artifacts = project["artifacts"]
    st.metric("Registered artifacts", len(artifacts))
    if artifacts:
        st.dataframe(pd.DataFrame(artifacts)[["id","title","type","stage","source"]], use_container_width=True, hide_index=True)
    else:
        st.info("No project artifacts yet. Add the first output above.")

st.divider(); st.subheader("💾 Project snapshot")
export_col, import_col = st.columns(2)
with export_col:
    st.download_button("⬇️ Export Research OS project JSON", to_json(project), "scimantra_research_os_project.json", "application/json", width="stretch")
with import_col:
    uploaded = st.file_uploader("Import a Research OS JSON snapshot", type=["json"], label_visibility="collapsed")
    if uploaded is not None and st.button("Import snapshot", width="stretch"):
        try:
            imported = from_json(uploaded.getvalue().decode("utf-8"))
            st.session_state.os_project_data = imported
            st.session_state.os_project = imported["project"]["name"]
            st.session_state.os_question = imported["project"]["question"]
            st.rerun()
        except (UnicodeDecodeError, ValueError) as exc: st.error(str(exc))

st.divider(); st.subheader("🛡️ Research OS control layer")
controls=[("🔗 Evidence provenance","Trace claims to results, analyses, datasets and source evidence."),("🛡️ Scientific integrity","Find contradictions, unsupported claims and verification gaps."),("🧪 Design quality","Audit controls, confounding, bias, assumptions and robustness."),("🧐 Reviewer readiness","Surface likely reviewer attacks before submission.")]
cols=st.columns(4)
for i,(title,desc) in enumerate(controls):
    with cols[i]: st.markdown(f"<div class='card'><h3>{title}</h3><p>{desc}</p></div>",unsafe_allow_html=True)

st.divider(); st.subheader("Connected intelligence chain")
st.markdown("**Literature → Evidence Matrix → Novelty → Research Gap → Research Forge → Experiment → Design Optimization → Pilot → Falsification → Causal/Bias Audit → Statistics → Robustness → Reproducibility → Provenance → Integrity → Claim Stress Test → Evidence Sufficiency → Generalizability → Mechanism → Prior Art → Peer Review → Decision → Next Study**")
st.success("Research OS is active. Start with Research Forge, then register important outputs and connect them in Data Linkage.")
st.caption("Decision support only. SciMantra does not certify scientific validity, novelty, causality, or publication acceptance.")
