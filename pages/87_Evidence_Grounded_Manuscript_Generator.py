"""SciMantra Research OS — Evidence-Grounded Manuscript Generator."""
import streamlit as st
from src.scimantra.evidence_grounded_manuscript import SECTIONS, draft_section, audit_draft

st.set_page_config(page_title="Evidence-Grounded Manuscript", page_icon="📝", layout="wide")
st.title("📝 Evidence-Grounded Manuscript Generator")
st.caption("Build manuscript sections from registered claims, evidence anchors and references.")
st.warning("This generator structures researcher-provided evidence into a draft. It does not invent evidence, verify scientific truth, or guarantee citation accuracy.")

section = st.selectbox("Manuscript section", SECTIONS)
claims_text = st.text_area("Claims — one per line", placeholder="State the finding or argument you want to make")
evidence_text = st.text_area("Verified evidence anchors — ID | statement", placeholder="EVID-001 | Treatment reduced concentration by 25%")
citation_text = st.text_area("Citation anchors — ID | title", placeholder="REF-001 | Author et al. (2025) study title")

claims=[]
for i,line in enumerate(claims_text.splitlines(),1):
    if line.strip(): claims.append({"claim":line.strip(),"section":section,"evidence_id":f"EVID-{i:03d}"})
evidence=[]
for i,line in enumerate(evidence_text.splitlines(),1):
    parts=line.split("|",1); evidence.append({"id":parts[0].strip() if parts else f"EVID-{i:03d}","statement":parts[1].strip() if len(parts)>1 else line.strip(),"verified":True})
citations=[]
for i,line in enumerate(citation_text.splitlines(),1):
    parts=line.split("|",1); citations.append({"id":parts[0].strip() if parts else f"REF-{i:03d}","title":parts[1].strip() if len(parts)>1 else line.strip()})

if st.button("Generate evidence-grounded outline", type="primary"):
    result=draft_section(section,evidence,claims,citations)
    st.subheader("Draft")
    st.code(result["text"], language="markdown")
    st.download_button("Download Markdown", result["text"], f"scimantra_{section.lower()}_draft.md", "text/markdown")

st.divider(); st.subheader("Draft audit")
text=st.text_area("Paste/edit draft for a structural audit", height=180)
a=audit_draft(text,evidence,claims)
c1,c2,c3=st.columns(3); c1.metric("Words",a["word_count"]); c2.metric("Evidence anchors",a["evidence_anchors"]); c3.metric("Claim records",a["claim_records"])
st.caption(a["warning"])
st.caption("Module 87 · Evidence → Claims → Manuscript drafting layer.")
