"""SciMantra Research OS launcher.

This launcher intentionally lives outside the repository-level ``pages/`` directory.
The main SciMantra app still uses ``pages/`` for its legacy multipage application,
while Research OS uses Streamlit's Page/navigation API. Keeping this launcher in a
separate directory prevents Streamlit Cloud from auto-discovering the legacy pages
before the Research OS router initializes.
"""
from pathlib import Path
import re
import sys

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
APP_DIR = Path(__file__).resolve().parent
PAGES_DIR = ROOT / "pages"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.scimantra.research_os_state import (
    STAGE_NAMES,
    STATUS_VALUES,
    add_artifact,
    from_json,
    new_project,
    progress,
    set_stage,
    to_json,
)

st.set_page_config(
    page_title="SciMantra Research OS",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)


def _page_title(path: Path) -> str:
    name = re.sub(r"^\d+_", "", path.stem)
    return re.sub(r"_+", " ", name).strip() or path.stem


def _page_source(path: Path) -> str:
    # st.Page paths are relative to this entrypoint; ../pages is intentional.
    return str(path.relative_to(APP_DIR))


def _url_path(path: Path) -> str:
    return re.sub(r"[^a-z0-9_-]+", "-", path.stem.lower()).strip("-")


def _build_pages():
    files = sorted(PAGES_DIR.glob("*.py"), key=lambda p: p.name.lower())
    research_os = [
        p for p in files
        if re.match(r"^(100|101|102|103|104|105|106|107|108|109|110|111|112|113|114|115|116|118|119|120)_", p.name)
    ]
    core = [p for p in files if p not in research_os]
    return {
        "SciMantra Research OS": [
            st.Page(_home, title="Research OS Home", icon="🔬", url_path="research-os-home", default=True),
            *[
                st.Page(_page_source(p), title=_page_title(p), icon="🧠", url_path=_url_path(p))
                for p in research_os
            ],
        ],
        "Research Tools": [
            *[
                st.Page(_page_source(p), title=_page_title(p), icon="🧪", url_path=_url_path(p))
                for p in core
            ],
        ],
    }


STAGES = [
    ("01", "Research Question", "Define the problem, scope and question", "❓", "56_Research_Question_Hypothesis_Forge"),
    ("02", "Literature", "Retrieve and map evidence", "📚", "52_Literature_Evidence_Retriever"),
    ("03", "Hypothesis", "Create falsifiable hypotheses", "💡", "56_Research_Question_Hypothesis_Forge"),
    ("04", "Experiment", "Design experiments and controls", "🧪", "57_Research_Experiment_Architect"),
    ("05", "Data", "Extract and organize evidence", "🗃️", "53_Evidence_Extraction_Engine"),
    ("06", "Analysis", "Audit assumptions and robustness", "📊", "64_Statistical_Assumption_Analysis_Choice_Lab"),
    ("07", "Evidence", "Synthesize evidence and gaps", "🔗", "54_Evidence_Synthesis_Gap_Engine"),
    ("08", "Claims", "Stress-test scientific claims", "🛡️", "69_Research_Claim_Stress_Test"),
    ("09", "Manuscript", "Build evidence-grounded writing", "📝", "49_Research_Manuscript_Studio"),
    ("10", "Peer Review", "Challenge the study before submission", "🧐", "74_Hostile_Peer_Review_Simulator"),
    ("11", "Submission", "Assess readiness and decision risks", "📤", "75_Research_Decision_Orchestrator"),
    ("12", "Next Study", "Turn findings into the next research cycle", "🔄", "75_Research_Decision_Orchestrator"),
]


def _home():
    if "os_project_data" not in st.session_state:
        st.session_state.os_project_data = new_project()
    project = st.session_state.os_project_data

    with st.sidebar:
        st.title("🔬 SciMantra")
        st.caption("Research Operating System")
        st.divider()
        name = st.text_input("Project name", project["project"]["name"])
        question = st.text_area("Central research question", project["project"]["question"], placeholder="What are you trying to discover?")
        if name != project["project"]["name"] or question != project["project"]["question"]:
            project["project"]["name"] = name.strip() or "My Research Project"
            project["project"]["question"] = question.strip()
            st.session_state.os_project_data = project
        st.divider()
        st.success("Shared project state is active for this Streamlit session. Export the snapshot to preserve it.")

    st.title("🔬 SciMantra Research OS")
    st.caption("From research idea to evidence, manuscript, peer-review challenge and the next study.")
    st.subheader("🚀 Start here")
    cols = st.columns(6)
    cards = [
        (cols[0], "❓ Research Forge", "Questions + falsifiable hypotheses", "56_Research_Question_Hypothesis_Forge"),
        (cols[1], "📚 Literature", "Retrieve and map evidence", "52_Literature_Evidence_Retriever"),
        (cols[2], "🗂️ Workspace", "Manage lifecycle + outputs", "76_Unified_Research_Project_Workspace"),
        (cols[3], "🔗 Data Linkage", "Connect research artifacts", "79_Cross_Tool_Data_Linkage"),
        (cols[4], "⚙️ Automation", "See what to do next", "81_Research_Workflow_Automation"),
        (cols[5], "🧭 Next Action", "Prioritize the next research move", "106_Research_OS_Next_Action_Engine"),
    ]
    page_map = {p.stem: p for p in PAGES_DIR.glob("*.py")}
    for col, title, desc, stem in cards:
        with col:
            st.markdown(f"**{title}**  \n{desc}")
            page = page_map.get(stem)
            if page:
                st.page_link(_url_path(page), label="Open →")

    p = progress(project)
    completion = round(100 * p["complete"] / p["total"])
    a, b, c, d = st.columns(4)
    a.metric("Completion", f"{completion}%")
    b.metric("Complete", p["complete"])
    c.metric("In progress", p["in_progress"])
    d.metric("Blocked", p["blocked"])
    st.progress(completion / 100)

    st.subheader("Research lifecycle")
    for i, (num, name, desc, icon, stem) in enumerate(STAGES):
        if i % 4 == 0:
            row = st.columns(4)
        with row[i % 4]:
            status = project["stages"][name]["status"]
            st.markdown(f"### {icon} {name}")
            st.caption(f"{num} · {status}")
            new = st.selectbox("Status", STATUS_VALUES, index=STATUS_VALUES.index(status), key=f"os_status_{num}", label_visibility="collapsed")
            if new != status:
                project = set_stage(project, name, status=new)
                st.session_state.os_project_data = project
            page = page_map.get(stem)
            if page:
                st.page_link(_url_path(page), label="Open workbench →")

    st.divider()
    st.subheader("🧩 Project data bus")
    left, right = st.columns([1.15, 1])
    with left:
        with st.form("artifact_form"):
            t = st.text_input("Artifact title", placeholder="e.g., Literature evidence matrix")
            typ = st.selectbox("Artifact type", ["Question", "Hypothesis", "Literature", "Dataset", "Analysis", "Result", "Figure", "Table", "Claim", "Protocol", "Manuscript", "Review", "Other"])
            stage = st.selectbox("Research stage", STAGE_NAMES)
            src = st.text_input("Source / file / DOI")
            desc = st.text_area("Description")
            submit = st.form_submit_button("➕ Add to project", type="primary")
        if submit:
            try:
                project = add_artifact(project, t, typ, stage, src, desc)
                st.session_state.os_project_data = project
                st.success("Artifact added.")
            except ValueError as exc:
                st.error(str(exc))
    with right:
        arts = project["artifacts"]
        st.metric("Registered artifacts", len(arts))
        st.dataframe(pd.DataFrame(arts)[["id", "title", "type", "stage", "source"]] if arts else pd.DataFrame(columns=["id", "title", "type", "stage", "source"]), use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("💾 Project snapshot")
    e, i = st.columns(2)
    with e:
        st.download_button("⬇️ Export JSON", to_json(project), "scimantra_research_os_project.json", "application/json", width="stretch")
    with i:
        uploaded = st.file_uploader("Import JSON", type=["json"])
        if uploaded is not None and st.button("Import snapshot"):
            try:
                st.session_state.os_project_data = from_json(uploaded.getvalue().decode("utf-8"))
                st.rerun()
            except (UnicodeDecodeError, ValueError) as exc:
                st.error(str(exc))

    st.divider()
    st.subheader("🛡️ Control layer")
    st.write("Evidence provenance · Scientific integrity · Design quality · Reviewer readiness")
    st.success("Research OS is active. Start with Research Forge, register outputs, connect them, then use Next Action to prioritize the most important remaining work.")
    st.caption("Decision support only. SciMantra does not certify scientific validity, novelty, causality, or publication acceptance.")


pg = st.navigation(_build_pages(), position="sidebar", expanded=True)
pg.run()
