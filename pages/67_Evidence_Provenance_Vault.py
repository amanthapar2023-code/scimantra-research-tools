import pandas as pd
import streamlit as st

from scimantra.provenance_vault import OBJECT_TYPES, RELATIONS, audit_objects, export_vault, link_row, object_row, provenance_completeness, trace_claim

st.set_page_config(page_title="Evidence Provenance Vault | SciMantra", layout="wide")
st.title("Research Evidence Provenance Vault")
st.caption("Build a traceable chain from manuscript claims back to the evidence that produced them.")
st.warning("Integrity rule: provenance records are researcher-supplied. SciMantra does not authenticate sources or certify that a claim is scientifically true.")

if "provenance_objects" not in st.session_state:
    st.session_state.provenance_objects = [object_row()]
if "provenance_links" not in st.session_state:
    st.session_state.provenance_links = [link_row()]

st.subheader("1. Register evidence objects")
for i, obj in enumerate(st.session_state.provenance_objects):
    with st.expander(f"Object {i + 1}: {obj.get('Title / label') or 'Unnamed'}", expanded=i == 0):
        c1, c2 = st.columns(2)
        obj["ID"] = c1.text_input("Stable ID", obj["ID"], key=f"oid_{i}")
        obj["Type"] = c2.selectbox("Object type", OBJECT_TYPES, index=OBJECT_TYPES.index(obj["Type"]) if obj["Type"] in OBJECT_TYPES else 0, key=f"otype_{i}")
        obj["Title / label"] = st.text_input("Title / label", obj["Title / label"], key=f"otitle_{i}")
        obj["Source / location"] = st.text_input("Source / location", obj["Source / location"], key=f"osource_{i}")
        c3, c4 = st.columns(2)
        obj["Version"] = c3.text_input("Version / run", obj["Version"], key=f"oversion_{i}")
        obj["Owner"] = c4.text_input("Owner / analyst", obj["Owner"], key=f"oowner_{i}")
        obj["Notes"] = st.text_area("Notes", obj["Notes"], key=f"onotes_{i}")

if st.button("+ Add evidence object"):
    st.session_state.provenance_objects.append(object_row())
    st.rerun()

st.subheader("2. Connect the provenance chain")
ids = [str(o.get("ID", "")).strip() for o in st.session_state.provenance_objects if str(o.get("ID", "")).strip()]
for i, link in enumerate(st.session_state.provenance_links):
    c1, c2, c3 = st.columns([1, 1, 1])
    link["From ID"] = c1.selectbox("From", [""] + ids, index=([""] + ids).index(link["From ID"]) if link["From ID"] in ids else 0, key=f"from_{i}")
    link["Relation"] = c2.selectbox("Relation", RELATIONS, index=RELATIONS.index(link["Relation"]) if link["Relation"] in RELATIONS else 0, key=f"rel_{i}")
    link["To ID"] = c3.selectbox("To", [""] + ids, index=([""] + ids).index(link["To ID"]) if link["To ID"] in ids else 0, key=f"to_{i}")
    link["Evidence / rationale"] = st.text_input("Why is this relationship valid?", link["Evidence / rationale"], key=f"lrationale_{i}")

if st.button("+ Add provenance link"):
    st.session_state.provenance_links.append(link_row())
    st.rerun()

objects = st.session_state.provenance_objects
links = st.session_state.provenance_links
audit = audit_objects(objects, links)

st.subheader("3. Provenance health")
a, b, c, d = st.columns(4)
a.metric("Completeness", f"{provenance_completeness(objects, links)}%")
b.metric("Objects", audit["objects"])
c.metric("Links", audit["links"])
d.metric("Dangling links", audit["dangling"])

if audit["duplicates"]:
    st.error("Duplicate IDs: " + ", ".join(audit["duplicates"]))
if audit["missing_source"]:
    st.warning(f"{audit['missing_source']} registered object(s) have no source/location.")
if audit["isolated"]:
    st.info(f"{audit['isolated']} object(s) are currently isolated from the provenance graph.")

st.subheader("4. Claim → evidence trace")
claim_ids = [str(o.get("ID")) for o in objects if o.get("Type") == "Claim" and str(o.get("ID", "")).strip()]
if claim_ids:
    selected = st.selectbox("Select a claim", claim_ids)
    trace = trace_claim(selected, objects, links)
    st.dataframe(pd.DataFrame([{k: x.get(k, "") for k in ["ID", "Type", "Title / label", "Source / location", "Version"]} for x in trace]), use_container_width=True, hide_index=True)
else:
    st.info("Register at least one object with type 'Claim' to generate a claim-to-evidence trace.")

st.download_button("Download provenance vault (Markdown)", export_vault(objects, links), "scimantra_provenance_vault.md", "text/markdown", use_container_width=True)
