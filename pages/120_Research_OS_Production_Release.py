"""SciMantra Research OS — Phase 120 production release gate."""
import json
import streamlit as st

from scimantra.research_os_beta import REQUIRED_CHECKS, gate
from scimantra.research_os_health import readiness_report
from scimantra.research_os_release import VERSION, release_manifest
from scimantra.research_os_data_bus import new_bus

st.set_page_config(page_title="Research OS Production Release", page_icon="🚀", layout="wide")
st.title("🚀 SciMantra Research OS — Production Release")
st.caption(f"Release {VERSION} · Production channel")

secrets = st.secrets if hasattr(st, "secrets") else {}
bus = st.session_state.get("research_os_bus") or new_bus("", "Research OS")
health = readiness_report(secrets, bus)
checks = {name: bool(st.session_state.get(f"beta_{name}", False)) for name in REQUIRED_CHECKS}
beta = gate(health, checks)
manifest = release_manifest(health, beta)

a,b,c = st.columns(3)
a.metric("Version", VERSION)
b.metric("Health", "READY" if health["ready"] else "BLOCKED")
c.metric("Release", "GO" if manifest["release_ready"] else "HOLD")

if manifest["release_ready"]:
    st.success("🟢 PRODUCTION RELEASE GATE PASSED")
    st.write("The software release checks are satisfied. Continue normal operational monitoring and collect beta/user feedback.")
else:
    st.error("🔴 PRODUCTION RELEASE ON HOLD")
    if beta["missing_checks"]:
        st.write("Remaining beta checks:")
        for item in beta["missing_checks"]: st.write(f"• {item}")
    if beta["health_failures"]: st.write(f"Health failures: {beta['health_failures']}")

st.subheader("Release scope")
st.write(manifest["scope"])
st.subheader("Release limitations")
for item in manifest["limitations"]: st.write(f"• {item}")

with st.expander("Release manifest"):
    st.code(json.dumps(manifest, indent=2, ensure_ascii=False), language="json")

st.info("This gate verifies software/deployment readiness. It is not a scientific validation or publication-acceptance prediction.")
