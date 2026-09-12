"""SciMantra Research OS — Phase 119 beta readiness checklist."""
import streamlit as st
from scimantra.research_os_health import readiness_report
from scimantra.research_os_state import STAGE_NAMES

st.set_page_config(page_title="Research OS Beta Readiness", page_icon="🚀", layout="wide")
st.title("🚀 SciMantra Research OS — Beta Readiness")
st.caption("A practical launch checklist for a controlled beta. Scientific validity and publication outcomes remain the researcher's responsibility.")

if "beta_checks" not in st.session_state:
    st.session_state.beta_checks = {
        "Core workflow tested": False,
        "Cloud persistence tested": False,
        "Authentication/project isolation tested": False,
        "Export/import tested": False,
        "Research OS health page reviewed": False,
        "Sample project completed end-to-end": False,
        "Privacy/secret configuration reviewed": False,
        "User feedback channel prepared": False,
    }

st.subheader("Automated gate")
report = readiness_report(st.secrets if hasattr(st, "secrets") else {}, st.session_state.get("research_os_bus"))
a, b, c = st.columns(3)
a.metric("Health gate", "READY" if report["ready"] else "BLOCKED")
b.metric("Warnings", report["warnings"])
c.metric("Lifecycle stages", len(STAGES) if False else len(STAGE_NAMES))

st.subheader("Beta checklist")
for label in list(st.session_state.beta_checks):
    st.session_state.beta_checks[label] = st.checkbox(label, value=st.session_state.beta_checks[label], key=f"beta_{label}")

completed = sum(st.session_state.beta_checks.values())
total = len(st.session_state.beta_checks)
st.progress(completed / total if total else 0)
st.write(f"**{completed}/{total} manual beta checks complete**")

if report["ready"] and completed == total:
    st.success("🟢 BETA READY — all configured checks are complete.")
else:
    st.warning("🟡 NOT YET READY — complete the remaining checks and resolve any blocking health failures before inviting beta users.")

with st.expander("Release notes to verify"):
    st.markdown("""
- Keep Supabase and other credentials in deployment secrets, never source code.
- Test a fresh user, an existing user, and an unauthorized project access attempt.
- Test an empty project, a normal project, and a malformed import.
- Verify cloud restore and conflict protection before relying on persistent state.
- Use representative research projects before broad public release.
- Treat all scientific scores and recommendations as decision-support outputs, not guarantees.
""")
