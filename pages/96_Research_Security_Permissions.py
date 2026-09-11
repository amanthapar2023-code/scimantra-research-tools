"""SciMantra Research OS — Research Security & Permissions."""
import pandas as pd
import streamlit as st
from src.scimantra.research_security_permissions import ROLES,can,audit_members

st.set_page_config(page_title="Research Security & Permissions",page_icon="🔐",layout="wide")
st.title("🔐 Research Security & Permissions")
st.caption("Define project-level roles and what each role may view, edit, approve, export or manage.")
st.warning("This is a permission-policy prototype. It does not enforce authentication or protect production data until connected to the application's identity/database layer.")
if "security_members" not in st.session_state: st.session_state.security_members=[]

with st.form("security_member"):
    c=st.columns(3); name=c[0].text_input("Member"); role=c[1].selectbox("Role",list(ROLES)); scope=c[2].text_input("Project / scope",value="Current project")
    if st.form_submit_button("Add member",type="primary"): st.session_state.security_members.append({"name":name,"role":role,"scope":scope})

r=audit_members(st.session_state.security_members); a,b,c=st.columns(3); a.metric("Members",r["members"]); b.metric("PI/Admin",r["admins"]); c.metric("Unknown roles",len(r["unknown_roles"]))

st.subheader("Role permission matrix")
rows=[]
for role,p in ROLES.items(): rows.append({"Role":role,**{k.replace("_"," ").title():"Allowed" if v else "Restricted" for k,v in p.items()}})
st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)

st.subheader("Current project members")
if st.session_state.security_members: st.dataframe(pd.DataFrame(st.session_state.security_members),use_container_width=True,hide_index=True)
else: st.info("No members assigned yet.")

st.subheader("Permission check")
c=st.columns(2); selected=c[0].selectbox("Role to test",list(ROLES)); action=c[1].selectbox("Action",["view","edit","approve","export","manage"])
st.success(f"{selected}: {'ALLOWED' if can(selected,action) else 'RESTRICTED'} for {action}.")
st.caption("Module 96 · Security policy model · enforcement requires production identity and database integration.")
