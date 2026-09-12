"""SciMantra Research OS launch and integration hub.

This page keeps the existing SciMantra Streamlit application as the main shell
while providing a safe bridge to the separately deployed Research OS app.
The Research OS URL is intentionally configurable so deployment coordinates
are never hard-coded into the repository.
"""

import os
import streamlit as st


st.set_page_config(
    page_title="Research OS Launch Hub",
    page_icon="🚀",
    layout="wide",
)

DEFAULT_URL = os.getenv("SCIMANTRA_RESEARCH_OS_URL", "").strip().rstrip("/")
if "research_os_url" not in st.session_state:
    st.session_state.research_os_url = DEFAULT_URL


def _normalise_url(value: str) -> str:
    value = value.strip()
    if not value:
        return ""
    if not value.startswith(("https://", "http://")):
        value = "https://" + value
    return value.rstrip("/")


st.title("🚀 SciMantra Research OS")
st.caption(
    "Launch the Research Operating System from the existing SciMantra platform "
    "without rebuilding the research engine or duplicating the Android logic."
)

st.info(
    "Recommended architecture: SciMantra remains the main platform; Research OS "
    "runs as its own Streamlit entrypoint and is opened from this integrated hub. "
    "The same Research OS URL can later be wrapped by an Android client."
)

left, right = st.columns([1.35, 1])
with left:
    st.subheader("1. Connect the deployed Research OS")
    url = st.text_input(
        "Research OS URL",
        value=st.session_state.research_os_url,
        placeholder="https://your-research-os.streamlit.app",
        help="Paste the public Streamlit URL created for research_os_app/research_os.py.",
    )
    if st.button("Save Research OS URL", type="primary", width="stretch"):
        clean = _normalise_url(url)
        if not clean:
            st.error("Enter the public Research OS URL first.")
        else:
            st.session_state.research_os_url = clean
            st.success("Research OS connection saved for this session.")

    connected_url = st.session_state.research_os_url
    if connected_url:
        st.link_button("🔬 Open Research OS", connected_url, type="primary", width="stretch")
        st.caption(f"Connected endpoint: {connected_url}")
    else:
        st.warning("No Research OS URL is configured yet.")

with right:
    st.subheader("2. Platform architecture")
    st.markdown(
        """
        **SciMantra**
        - Laboratory & environmental tools
        - Statistics & data analysis
        - Publication workflows
        - Project/account layer

        **Research OS**
        - Research question
        - Literature & evidence
        - Hypothesis
        - Experiment
        - Data & analysis
        - Claims & manuscript
        - Peer review & next study
        """
    )

st.divider()
st.subheader("🌐 Website launch")
web_cols = st.columns(3)
web_cols[0].metric("Main platform", "SciMantra")
web_cols[1].metric("Research engine", "Research OS")
web_cols[2].metric("Deployment model", "Separate Streamlit app")

if connected_url:
    st.markdown("### Public launch")
    st.link_button("Open Research OS website ↗", connected_url, width="stretch")
else:
    st.markdown(
        "Deploy `research_os_app/research_os.py` on Streamlit Community Cloud, "
        "then paste its public URL above."
    )

st.divider()
st.subheader("📱 Android strategy")
st.markdown(
    "The Android version should initially act as a client shell around the same "
    "web platform. This avoids maintaining a second scientific engine in Kotlin. "
    "Once the web workflow is stable, the Android shell can add native navigation, "
    "notifications, file selection and account features."
)

android_steps = [
    ("01", "Web first", "Validate Research OS as the primary research workflow."),
    ("02", "Integrated SciMantra", "Keep the existing SciMantra app as the main product shell."),
    ("03", "Android shell", "Wrap the web experience and preserve the same backend/workflows."),
    ("04", "Native upgrades", "Add device-specific capabilities only where they improve the workflow."),
]
cols = st.columns(4)
for col, (num, title, desc) in zip(cols, android_steps):
    with col:
        st.markdown(f"### {num} · {title}")
        st.caption(desc)

st.divider()
st.subheader("🧩 Embed inside SciMantra or WordPress")
st.code(
    '<iframe src="YOUR_RESEARCH_OS_URL?embed=true" '
    'style="width:100%;height:900px;border:0;" '
    'allow="clipboard-write"></iframe>',
    language="html",
)
st.caption(
    "Replace YOUR_RESEARCH_OS_URL with the deployed Research OS address. "
    "Use the same public URL for the website launch and future Android client."
)

st.divider()
st.subheader("🛡️ Launch checklist")
checks = [
    ("Research OS entrypoint", "research_os_app/research_os.py"),
    ("Repository", "amanthapar2023-code/scimantra-research-tools"),
    ("Existing SciMantra app", "app.py"),
    ("Integration page", "124_Research_OS_Launch_Hub.py"),
    ("URL configuration", "SCIMANTRA_RESEARCH_OS_URL"),
]
for label, value in checks:
    st.write(f"**{label}:** `{value}`")

st.success(
    "Phase 124 is ready: the Research OS can now be launched from the existing "
    "SciMantra application without changing the stable core app architecture."
)
