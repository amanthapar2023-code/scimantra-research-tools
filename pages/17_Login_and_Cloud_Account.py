import streamlit as st

from src.scimantra.cloud import client, configured, current_user, sign_in, sign_out, sign_up, load_profile, save_profile

st.set_page_config(page_title="SciMantra Account", page_icon="👤", layout="wide")

st.title("👤 SciMantra Account & Cloud Workspace")
st.caption("Optional managed authentication with Supabase. The app continues to work locally without cloud configuration.")

if not configured(st.secrets):
    st.info("Cloud authentication is not configured yet. Add SUPABASE_URL and SUPABASE_ANON_KEY to your deployment secrets after creating the Supabase project and applying supabase/schema.sql.")
    st.subheader("What this enables")
    for item in [
        "Secure email/password authentication handled by Supabase Auth",
        "Private researcher profile",
        "Cloud project persistence",
        "Project membership and collaboration foundation",
        "Cloud subscription status",
        "Future verified billing webhooks",
    ]:
        st.write(f"✅ {item}")
    st.warning("Never store passwords, payment card details, provider signing secrets or API keys in source code or Streamlit session state.")
    st.stop()

supa = client(st.secrets)
user = current_user(supa)

if user is None:
    login_tab, signup_tab = st.tabs(["🔑 Sign in", "🆕 Create account"])
    with login_tab:
        with st.form("login"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Sign in", type="primary")
        if submit:
            try:
                sign_in(supa, email.strip(), password)
                st.success("Signed in successfully. Refreshing workspace…")
                st.rerun()
            except Exception as exc:
                st.error(f"Sign-in failed: {exc}")
    with signup_tab:
        with st.form("signup"):
            name = st.text_input("Full name")
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Password", type="password", key="signup_password")
            confirmation = st.text_input("Confirm password", type="password")
            submit = st.form_submit_button("Create account", type="primary")
        if submit:
            if password != confirmation:
                st.error("Passwords do not match.")
            elif len(password) < 8:
                st.error("Use a password of at least 8 characters.")
            else:
                try:
                    sign_up(supa, email.strip(), password, name.strip())
                    st.success("Account created. If email confirmation is enabled, check your email before signing in.")
                except Exception as exc:
                    st.error(f"Account creation failed: {exc}")
    st.stop()

profile = load_profile(supa, user.id)

c1, c2 = st.columns([3, 1])
with c1:
    st.subheader(f"Welcome, {profile.get('full_name') or user.email}")
    st.caption(user.email or "Authenticated researcher")
with c2:
    if st.button("🚪 Sign out"):
        sign_out(supa)
        st.rerun()

with st.form("profile"):
    full_name = st.text_input("Full name", profile.get("full_name", ""))
    institution = st.text_input("Institution / Lab", profile.get("institution", ""))
    save = st.form_submit_button("💾 Save profile")
if save:
    try:
        save_profile(supa, user.id, full_name.strip(), institution.strip(), profile.get("avatar_url", ""))
        st.success("Profile saved to your cloud account.")
    except Exception as exc:
        st.error(f"Could not save profile: {exc}")

st.divider()
st.subheader("🔒 Account security")
st.write("Authentication is delegated to Supabase Auth; SciMantra does not store your password in the application database.")
st.write("For production billing, subscription changes should be written only by a trusted server-side webhook after signature verification.")
