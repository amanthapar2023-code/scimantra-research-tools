"""Unified SciMantra / Research OS launch experience."""

import os
import streamlit as st

st.set_page_config(page_title="SciMantra Research OS", page_icon="🔬", layout="wide")

DEFAULT_URL = os.getenv("SCIMANTRA_RESEARCH_OS_URL", "").strip().rstrip("/")
if "research_os_url" not in st.session_state:
    st.session_state.research_os_url = DEFAULT_URL
if "research_os_mode" not in st.session_state:
    st.session_state.research_os_mode = "Integrated view"


def normalise_url(value: str) -> str:
    value = value.strip()
    if not value:
        return ""
    if not value.startswith(("https://", "http://")):
        value = "https://" + value
    return value.rstrip("/")


def embed_url(value: str) -> str:
    separator = "&" if "?" in value else "?"
    return f"{value}{separator}embed=true"


st.markdown(
    """
    <style>
    .scim-hero{padding:1.7rem 2rem;border-radius:22px;
      background:linear-gradient(135deg,#e9f4ff 0%,#f8fbff 55%,#eefaf5 100%);
      border:1px solid #d8e8f5;margin-bottom:1.2rem}
    .scim-hero h1{margin:0;color:#0b2033;font-size:2.35rem}
    .scim-hero p{margin:.45rem 0 0;color:#486176;font-size:1.05rem}
    .launch-note{padding:1rem 1.1rem;border:1px solid #dfe8ee;border-radius:15px;
      background:#fff;margin:.5rem 0 1rem}
    iframe{border-radius:16px}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="scim-hero"><h1>🔬 SciMantra Research OS</h1>'
    '<p><b>One research platform.</b> Move from question → evidence → experiment → analysis → manuscript → peer review → next study.</p></div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("## 🔬 SciMantra")
    st.caption("Research Operating System")
    st.divider()
    mode = st.radio(
        "Research OS view",
        ["Integrated view", "Open full app", "Connection setup"],
        index=["Integrated view", "Open full app", "Connection setup"].index(st.session_state.research_os_mode),
    )
    st.session_state.research_os_mode = mode
    if st.session_state.research_os_url:
        st.success("Research OS connected")
    else:
        st.warning("Research OS URL not configured")
    st.caption("SciMantra remains the main platform; Research OS is the research workflow layer.")

connected_url = st.session_state.research_os_url

if mode == "Connection setup":
    st.subheader("🔗 Connect Research OS")
    st.write(
        "Paste the public Streamlit URL for the Research OS deployment. "
        "The URL is stored for this Streamlit session or can be supplied permanently "
        "through the `SCIMANTRA_RESEARCH_OS_URL` environment variable."
    )
    value = st.text_input(
        "Research OS URL",
        value=connected_url,
        placeholder="https://your-research-os.streamlit.app",
    )
    if st.button("Save connection", type="primary", width="stretch"):
        clean = normalise_url(value)
        if clean:
            st.session_state.research_os_url = clean
            st.success("Research OS connected. Switch to Integrated view.")
            st.rerun()
        else:
            st.error("Enter a valid Research OS URL.")
    st.divider()
    st.markdown("### Required deployment")
    st.code("research_os_app/research_os.py")
    st.caption("Deploy this entrypoint as the separate Research OS Streamlit app.")

elif not connected_url:
    st.subheader("🚀 Research OS is ready to connect")
    st.info(
        "The integration layer is installed. Deploy the Research OS entrypoint, "
        "then use Connection setup in the sidebar to connect it."
    )
    st.markdown("### Deployment target")
    st.code("research_os_app/research_os.py")
    st.link_button("Open Streamlit Community Cloud", "https://share.streamlit.io/", width="stretch")
    st.divider()
    st.subheader("What the unified experience will contain")
    cols = st.columns(4)
    for col, icon, title, desc in [
        (cols[0], "❓", "Question", "Define a precise research question."),
        (cols[1], "📚", "Evidence", "Map literature, gaps and provenance."),
        (cols[2], "🧪", "Experiment", "Build controls, replication and falsification."),
        (cols[3], "📝", "Publication", "Connect analysis, claims and manuscript."),
    ]:
        with col:
            st.markdown(f"### {icon} {title}")
            st.caption(desc)

elif mode == "Open full app":
    st.subheader("🔬 Research OS")
    st.caption("Full-screen Research OS deployment")
    st.link_button("Open Research OS in a new tab ↗", connected_url, type="primary", width="stretch")
    st.markdown(f'<div class="launch-note">Connected to <b>{connected_url}</b></div>', unsafe_allow_html=True)

else:
    st.subheader("🧠 Research OS — Integrated view")
    st.caption("Research OS is running inside the SciMantra experience.")
    st.markdown(
        '<div class="launch-note">Use the Research OS navigation below. '
        'Your scientific workflow remains in the same SciMantra product experience.</div>',
        unsafe_allow_html=True,
    )
    st.components.v1.iframe(embed_url(connected_url), height=1100, scrolling=True)
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        st.link_button("↗ Open full Research OS", connected_url, width="stretch")
    with c2:
        st.page_link("pages/124_Research_OS_Launch_Hub.py", label="🔄 Refresh integration", width="stretch")

st.divider()
st.subheader("📱 Android-ready architecture")
st.markdown(
    "The Android client can use this same Research OS endpoint instead of creating a second "
    "scientific implementation. Native Android features can be added later for authentication, "
    "notifications, camera/file capture and device integration."
)

st.caption(
    "Phase 125 · Unified launch layer · Scientific decision support only; this interface does not certify novelty, validity or publication acceptance."
)
