import streamlit as st
from src.scimantra.reproducibility_passport import passport_template, passport_audit, export_markdown

st.set_page_config(page_title="Reproducibility Passport | SciMantra", page_icon="🧬", layout="wide")
st.title("🧬 Research Reproducibility Passport")
st.caption("Create a machine-readable record of how the study was designed, measured, analyzed, and documented.")

title = st.text_input("Research title", value=st.session_state.get("ri_title", ""))
if "passport" not in st.session_state or st.session_state.passport.get("research_title") != title:
    st.session_state.passport = passport_template(title)

for name, data in st.session_state.passport["sections"].items():
    value = st.text_area(name, value=data.get("record", ""), help=data.get("description", ""), height=100, key="passport_" + name)
    data["record"] = value
    data["status"] = "RECORDED" if value.strip() else "MISSING"

audit = passport_audit(st.session_state.passport)
c1, c2, c3 = st.columns(3)
c1.metric("Passport sections", audit["total_sections"])
c2.metric("Recorded", audit["complete_sections"])
c3.metric("Coverage", f"{audit['coverage_percent']}%")

st.download_button("Download reproducibility passport (Markdown)", export_markdown(st.session_state.passport), "research_reproducibility_passport.md", "text/markdown")
st.info("A passport records provenance; it does not certify that a study is correct or reproducible. Missing information stays visible rather than being guessed.")
