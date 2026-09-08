import streamlit as st
import pandas as pd
from src.scimantra.novelty_radar import validate_direction
from src.scimantra.evidence_matrix import empty_record
from src.scimantra.research_intelligence import crossref_search

st.set_page_config(page_title="Novelty Collision Radar | SciMantra", page_icon="🛰️", layout="wide")
st.title("🛰️ Novelty Collision Radar")
st.caption("Stress-test a proposed research direction before you call it novel.")

st.info("This tool detects concept-level overlap and evidence patterns. It does not certify novelty, priority, originality, or publication acceptance.")
title = st.text_input("Research title", value=st.session_state.get("ri_title", ""))
direction = st.text_area("Proposed novelty / research direction", placeholder="Example: combine X and Y to solve Z under realistic conditions...")

records = st.session_state.get("em_records", [empty_record() for _ in range(5)])
papers = st.session_state.get("ri_papers", [])

if st.button("🔎 Run collision radar", type="primary", width="stretch"):
    if not title.strip() and not direction.strip():
        st.error("Enter a research title or proposed direction first.")
    else:
        with st.spinner("Comparing concepts and evidence patterns..."):
            if not papers and title.strip():
                try:
                    papers = crossref_search(title, rows=12)
                except Exception as exc:
                    papers = []
                    st.warning(f"Bibliographic search unavailable right now: {exc}")
            result = validate_direction(title, direction, papers, records)
            st.session_state.novelty_radar_result = result

result = st.session_state.get("novelty_radar_result")
if result:
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Radar status", result["status"])
    c2.metric("Close concept matches", len(result["collisions"]))
    c3.metric("Evidence patterns", len(result["patterns"]))

    st.subheader("⚠️ Research warnings")
    if result["warnings"]:
        for w in result["warnings"]: st.warning(w)
    else:
        st.success("No additional warning was triggered by the current evidence set.")

    st.subheader("Closest retrieved literature")
    if result["collisions"]:
        st.dataframe(pd.DataFrame(result["collisions"]), width="stretch", hide_index=True)
    else:
        st.write("No close title-level collisions were found in the available metadata.")

    st.subheader("Cross-paper patterns")
    if result["patterns"]:
        for p in result["patterns"]:
            with st.expander(f"{p['type']} — {p['signal']}"):
                st.write(p["verification"])
    else:
        st.write("No repeated evidence pattern was detected in the current matrix.")

    st.subheader("🧪 Novelty verification protocol")
    checks = [
        "Compare the closest papers by research question, not title alone.",
        "Compare intervention/technology, target system, variables, controls, and operating conditions.",
        "Check whether the claimed mechanism or explanation was already tested.",
        "Check whether the proposed combination has actually been reported together.",
        "Record exact source locations for every literature claim used in the novelty argument.",
        "State the remaining uncertainty instead of converting a low collision score into a novelty claim.",
    ]
    for i, check in enumerate(checks, 1): st.checkbox(check, key=f"novelty_check_{i}")

    export = pd.DataFrame(result["collisions"])
    st.download_button("⬇️ Export collision report", export.to_csv(index=False).encode(), "scimantra_novelty_collision_report.csv", "text/csv", width="stretch")
