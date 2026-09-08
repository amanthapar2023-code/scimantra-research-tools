import streamlit as st
import pandas as pd
from src.scimantra.research_copilot import project_health, project_snapshot

st.set_page_config(page_title="Research Project Copilot | SciMantra", page_icon="🧭", layout="wide")
st.title("🧭 Research Project Copilot")
st.caption("One cockpit for the evidence, design, reviewer, reproducibility and research-graph signals in your project.")

title = st.text_input("Research title", st.session_state.get("ri_title", ""))
st.write("Enter the current completion/readiness percentage for each project layer. 0 = not addressed, 100 = documented and reviewed by you.")
fields = ["Evidence coverage", "Design readiness", "Reviewer readiness", "Claim traceability", "Reproducibility coverage", "Research graph connectivity"]
keys = ["evidence", "design", "reviewer", "traceability", "reproducibility", "graph"]
vals = {}
for i, (label, key) in enumerate(zip(fields, keys)):
    vals[key] = st.slider(label, 0, 100, 50, key=f"pc_{key}")

if st.button("🚀 Build Project Cockpit", type="primary"):
    health = project_health(**vals)
    st.session_state.project_copilot_health = health

health = st.session_state.get("project_copilot_health")
if health:
    st.metric("Overall project health (planning heuristic)", f"{health['score']:.1f}/100", health["label"])
    st.dataframe(pd.DataFrame([{"Layer": k, "Readiness": v} for k, v in health["components"].items()]), width="stretch", hide_index=True)
    snapshot = project_snapshot(title, health, len(st.session_state.get("research_memory", [])))
    actions = snapshot["Priority actions"]
    st.subheader("Priority actions")
    if actions:
        for action in actions:
            st.write("• " + action)
    else:
        st.success("No layer is currently below the 70% planning threshold.")
else:
    st.info("Build the cockpit to see a unified project snapshot.")

st.warning("This is a project-management heuristic. A high score does not establish scientific validity, novelty, or publication acceptance.")
