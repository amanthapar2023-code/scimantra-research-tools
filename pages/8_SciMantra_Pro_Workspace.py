import io
from datetime import datetime

import pandas as pd
import streamlit as st

st.title("🚀 SciMantra Pro Workspace")
st.caption("A production workspace for research projects, reporting and future premium services.")

# Session-scoped workspace: no credentials or research data are written to the repository.
if "project_name" not in st.session_state:
    st.session_state.project_name = "My Research Project"
if "notes" not in st.session_state:
    st.session_state.notes = ""

with st.sidebar:
    st.subheader("Workspace")
    st.session_state.project_name = st.text_input("Project name", st.session_state.project_name)

section = st.selectbox(
    "Workspace module",
    ["Project Dashboard", "Research Notes", "Report Builder", "Pro Roadmap"],
)

if section == "Project Dashboard":
    st.subheader(st.session_state.project_name)
    c1, c2, c3 = st.columns(3)
    c1.metric("Workspace", "Active")
    c2.metric("Data privacy", "Session only")
    c3.metric("Export", "Available")
    st.info("Use Advanced Analysis and Data Analyzer for calculations. This workspace organizes your interpretation and reporting without changing the underlying scientific calculations.")
    st.markdown("### Recommended workflow")
    st.markdown("1. Upload and validate your dataset.\n2. Run replicate-aware analysis.\n3. Review statistics and figures.\n4. Record interpretation and limitations.\n5. Export a report for further editing.")

elif section == "Research Notes":
    st.subheader("Research Notes")
    st.session_state.notes = st.text_area(
        "Interpretation, observations, limitations or manuscript notes",
        st.session_state.notes,
        height=300,
        placeholder="Record observations here. Avoid entering passwords, API keys or confidential personal information.",
    )
    st.download_button(
        "⬇️ Download notes",
        st.session_state.notes.encode("utf-8"),
        file_name="scimantra_research_notes.txt",
        mime="text/plain",
    )

elif section == "Report Builder":
    st.subheader("Research Report Builder")
    title = st.text_input("Report title", st.session_state.project_name)
    author = st.text_input("Author / laboratory")
    abstract = st.text_area("Abstract / summary", height=160)
    findings = st.text_area("Key findings", height=180)
    limitations = st.text_area("Limitations", height=140)

    report = f"""{title}\n{'=' * len(title)}\n\nAuthor/Laboratory: {author}\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\nSUMMARY\n{abstract}\n\nKEY FINDINGS\n{findings}\n\nLIMITATIONS\n{limitations}\n\nRESEARCH NOTES\n{st.session_state.notes}\n\nSciMantra Research Tools\n"""
    st.download_button(
        "⬇️ Export report (.txt)",
        report.encode("utf-8"),
        file_name="scimantra_research_report.txt",
        mime="text/plain",
    )
    st.caption("This is an editable research-report draft, not a substitute for scientific review or journal formatting requirements.")

else:
    st.subheader("Production Roadmap")
    roadmap = pd.DataFrame(
        [
            ["Research workspace", "Live", "Project notes and report drafting"],
            ["Advanced experimental analysis", "Live", "Replicate-aware analysis and figures"],
            ["TEA & LCA", "Live", "Economic and sustainability screening"],
            ["Secure accounts", "Planned", "Requires an external authentication/database service"],
            ["Subscriptions", "Planned", "Requires Stripe or another payment provider"],
            ["AI research assistant", "Planned", "Requires a configured AI API key"],
            ["Similarity checker", "Planned", "Requires licensed/reference corpus or external provider"],
        ],
        columns=["Capability", "Status", "Implementation note"],
    )
    st.dataframe(roadmap, width="stretch", hide_index=True)
    st.warning("Do not market the planned similarity/AI-detection features as equivalent to Turnitin or another proprietary service until an appropriate licensed corpus/provider and validation study are implemented.")
