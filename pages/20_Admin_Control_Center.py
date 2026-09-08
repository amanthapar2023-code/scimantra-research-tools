"""Protected administrative view.

The page is intentionally read-mostly. Global subscription changes belong in
the trusted billing webhook/backend, not in a browser-facing Streamlit form.
"""
import streamlit as st

from src.scimantra.cloud import configured as cloud_configured, current_user, client

st.set_page_config(page_title="SciMantra Admin", page_icon="🛡️", layout="wide")
st.title("🛡️ SciMantra Admin Control Center")
st.caption("Restricted operational dashboard for platform administrators.")

user = current_user() if cloud_configured() else None
email = str((user or {}).get("email", ""))
try:
    admins = {x.strip().lower() for x in str(st.secrets.get("SCIMANTRA_ADMIN_EMAILS", "")).split(",") if x.strip()}
except Exception:
    admins = set()

if not email or email.lower() not in admins:
    st.error("Admin access is restricted.")
    st.info("Sign in with an authorized administrator account. Do not expose service-role credentials to users.")
    st.stop()

st.success(f"Authenticated administrator: {email}")

if not cloud_configured():
    st.warning("Supabase is not configured. Connect the production database to enable operational metrics.")
    st.stop()

supabase = client()
if supabase is None:
    st.error("Supabase client is unavailable.")
    st.stop()


def count_rows(table: str) -> int:
    try:
        result = supabase.table(table).select("id", count="exact").limit(1).execute()
        return int(result.count or 0)
    except Exception:
        return 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Researchers", count_rows("profiles"))
c2.metric("Projects", count_rows("projects"))
c3.metric("Subscriptions", count_rows("subscriptions"))
c4.metric("Datasets", count_rows("datasets"))

st.divider()
st.subheader("💳 Subscription operations")
try:
    result = supabase.table("subscriptions").select("user_id,plan,status,provider,current_period_end,updated_at").order("updated_at", desc=True).limit(100).execute()
    rows = result.data or []
    st.dataframe(rows, width="stretch", hide_index=True)
except Exception as exc:
    st.error(f"Could not load subscriptions: {exc}")

st.divider()
st.subheader("🔐 Production safeguards")
st.write("• Admin access is controlled by an allowlist stored in deployment secrets.")
st.write("• The service-role key is never displayed or stored in session state.")
st.write("• Subscription state should be changed by verified billing webhooks, not by this page.")
st.write("• Keep this page out of public documentation and restrict administrator accounts with MFA.")
