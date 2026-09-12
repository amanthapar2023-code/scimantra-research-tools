"""Phase 113 — Research OS Contract Adapter inspector."""
import json
import pandas as pd
import streamlit as st
from scimantra.research_os_contract_adapter import audit_registry, adapt_output, adapter_report

st.set_page_config(page_title="SciMantra — Contract Adapter", page_icon="🔌", layout="wide")
st.title("🔌 Phase 113 — Research OS Contract Adapter")
st.caption("Structural bridge between existing SciMantra tools and the canonical Research OS data contract.")
st.info("Adapters preserve the tool's scientific payload. This layer checks interoperability structure only; it does not validate scientific correctness.")

audit = audit_registry()
a,b,c,d = st.columns(4)
a.metric("Registered tools", audit["total"])
b.metric("Ready", audit["ready"])
c.metric("Needs adapter", audit["needs_adapter"])
d.metric("Coverage", f'{audit["coverage_pct"]}%')

st.divider()
tab1, tab2, tab3 = st.tabs(["🔍 Registry Audit", "📦 Adapt an Output", "📄 Export Report"])
with tab1:
    st.dataframe(pd.DataFrame(audit["rows"]), use_container_width=True, hide_index=True)
    if audit["coverage_pct"] == 100:
        st.success("All registered tools currently have an explicit adapter contract.")
    else:
        st.warning("Some tools require adapter work before they should participate in production synchronization.")
with tab2:
    names=list(sorted(audit["rows"], key=lambda x:x["tool"]))
    selected=st.selectbox("Source tool", [r["tool"] for r in names])
    r1,r2,r3=st.columns(3)
    project=r1.text_input("Project ID", "PROJECT-001"); artifact=r2.text_input("Artifact ID", "ART-113-001"); title=r3.text_input("Title", "Example output")
    r4,r5=st.columns(2)
    typ=r4.text_input("Artifact type", "Other"); status=r5.selectbox("Status", ["Draft","Active","Needs review","Verified","Archived"])
    payload_text=st.text_area("Scientific payload JSON", "{}")
    if st.button("Convert to canonical contract", type="primary"):
        try:
            payload=json.loads(payload_text)
            result=adapt_output(selected, project, artifact, title, typ, "", status, payload)
            if result["valid"]: st.success("Output is contract-compatible.")
            else: st.error("Contract validation failed.")
            st.json(result)
        except Exception as exc: st.error(str(exc))
with tab3:
    st.download_button("⬇️ Export adapter readiness report", adapter_report(), "scimantra_phase113_adapter_report.json", "application/json")
    st.code(json.dumps({"canonical_fields":["schema_version","project_id","artifact_id","artifact_type","stage","source_tool","status","created_at","payload"],"rule":"Preserve payload; normalize envelope."}, indent=2), language="json")

st.divider(); st.caption("Production boundary: the adapter layer prepares tool outputs for shared persistence; it does not silently modify research results.")
