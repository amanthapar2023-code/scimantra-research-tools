import streamlit as st
from src.scimantra.research_copilot import answer
from src.scimantra.research_os_state import new_project

st.set_page_config(page_title="Research Copilot 2.0", page_icon="🤖", layout="wide")
if "os_project_data" not in st.session_state: st.session_state.os_project_data=new_project()
project=st.session_state.os_project_data
st.title("🤖 Research Copilot 2.0")
st.caption("Ask the Research OS what needs attention, using the project's structured state.")
st.warning("The Copilot summarizes project signals and workflow rules. It does not establish scientific truth, causality, novelty, or publication acceptance.")
q=st.chat_input("Ask: What should I do next? What is weak? What evidence am I missing?")
if q:
    result=answer(q,project)
    st.chat_message("user").write(q)
    with st.chat_message("assistant"):
        st.write(result["answer"])
        st.caption(result["confidence"])
        if result["actions"]:
            st.markdown("**Relevant actions**")
            for a in result["actions"]: st.write(f"• **{a['priority']}** — {a['title']} ({a['stage']})")
else:
    st.subheader("Try asking")
    for text in ["What should I do next?","What is weak in my research?","What evidence am I missing?","What is blocking my project?","Am I ready to write the manuscript?"]: st.markdown(f"• {text}")
st.divider(); st.subheader("Current project")
st.write(project["project"].get("name","My Research Project"))
st.caption(project["project"].get("question","") or "No central research question entered yet.")
