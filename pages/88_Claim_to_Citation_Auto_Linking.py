"""SciMantra Research OS — Claim-to-Citation Auto-Linking."""
import pandas as pd
import streamlit as st
from src.scimantra.claim_citation_linker import link_claim, audit_links, export_markdown

st.set_page_config(page_title="Claim-to-Citation Auto-Linking", page_icon="🔗", layout="wide")
st.title("🔗 Claim-to-Citation Auto-Linking")
st.caption("Audit whether manuscript claims have explicit citation anchors.")
st.warning("Linkage is structural. A citation being attached to a claim does not prove that the source actually supports the claim.")

st.subheader("Citation registry")
citation_text=st.text_area("Citation IDs — one per line", placeholder="REF-001\nREF-002\nREF-003")
citations=[{"id":x.strip()} for x in citation_text.splitlines() if x.strip()]

st.subheader("Claims")
claim_text=st.text_area("Claim ID | claim text | citation IDs (comma separated)", height=180, placeholder="CLM-001 | Treatment reduced VOC concentration | REF-001, REF-002")
claims=[]
for line in claim_text.splitlines():
    p=[x.strip() for x in line.split("|",2)]
    if len(p)>=2:
        ids=[x.strip() for x in p[2].split(",")] if len(p)==3 and p[2].strip() else []
        claims.append(link_claim(p[0],p[1],ids))

if st.button("Audit claim → citation links", type="primary"):
    a=audit_links(claims,citations)
    c1,c2,c3=st.columns(3); c1.metric("Claims",a["claims"]); c2.metric("Citation coverage",f'{a["coverage"]}%'); c3.metric("Unlinked",a["unlinked"])
    if a["unlinked"]: st.error("Some claims have no citation anchor.")
    if a["broken_links"]: st.warning("Some citation IDs are not present in the registry.")
    st.dataframe(pd.DataFrame(a["rows"]),use_container_width=True,hide_index=True)
    md=export_markdown(a)
    st.download_button("Export link audit",md,"claim_citation_audit.md","text/markdown")

st.caption("Module 88 · Claim → Citation structural linkage · source support must still be checked by the researcher.")
