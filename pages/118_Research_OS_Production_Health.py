"""SciMantra Research OS — Phase 118 deployment health."""
import streamlit as st

from scimantra.research_os_health import readiness_report
from scimantra.research_os_data_bus import new_bus

st.set_page_config(page_title="Research OS Production Health", page_icon="🛡️", layout="wide")
st.title("🛡️ Research OS — Production Health")
st.caption("Deployment diagnostics and safe failure checks. This does not certify scientific validity.")

secrets = st.secrets if hasattr(st, "secrets") else {}
bus = st.session_state.get("research_os_bus") or new_bus("", "Research OS")
report = readiness_report(secrets, bus)

c1, c2, c3 = st.columns(3)
c1.metric("Release gate", "READY" if report["ready"] else "BLOCKED")
c2.metric("Warnings", report["warnings"])
c3.metric("Failures", report["failures"])

st.subheader("Health checks")
for item in report["checks"]:
    status = item["status"]
    icon = "✅" if status == "PASS" else "⚠️" if status == "WARN" else "❌"
    st.markdown(f"### {icon} {item['check']} — {status}")
    for issue in item.get("issues", []):
        st.write(f"• {issue}")

with st.expander("Technical audit"):
    st.json(report)

st.info("Production recommendation: keep cloud credentials in Streamlit Secrets, never in source code; investigate all FAIL states before release. WARN means the app can run but an optional capability is unavailable.")
