import streamlit as st

from src.scimantra.subscription import (
    FEATURES,
    FREE_FEATURES,
    PRO_FEATURES,
    checkout_configured,
    feature_label,
    get_subscription,
    set_plan,
)

st.set_page_config(page_title="SciMantra Plans", page_icon="💳", layout="wide")

st.title("💳 SciMantra Free vs Pro")
st.caption("A provider-neutral subscription and entitlement layer for the research platform.")

subscription = get_subscription(st.session_state)

with st.sidebar:
    st.header("Your plan")
    st.success("PRO" if subscription.is_pro else "FREE")
    st.caption(f"Status: {subscription.status}")
    if subscription.current_period_end:
        st.caption(f"Period ends: {subscription.current_period_end}")

c1, c2 = st.columns(2)
with c1:
    st.subheader("🆓 Free")
    st.markdown("### Research essentials")
    for feature in sorted(FREE_FEATURES):
        st.write(f"✅ {feature_label(feature)}")
    st.write("Built for exploring SciMantra and running core research tasks.")

with c2:
    st.subheader("⭐ Pro")
    st.markdown("### Full research workflow")
    for feature in sorted(PRO_FEATURES):
        st.write(f"🚀 {feature_label(feature)}")
    st.write("Designed for researchers who need the complete analysis, reporting and AI-assisted workflow.")

st.divider()
st.subheader("Feature access")
rows = []
for key, label in FEATURES.items():
    rows.append({"Feature": label, "Free": "✅" if key in FREE_FEATURES else "—", "Pro": "✅"})
st.dataframe(rows, width="stretch", hide_index=True)

st.divider()
st.subheader("🔐 Subscription status")
status_cols = st.columns(4)
status_cols[0].metric("Current plan", subscription.plan.upper())
status_cols[1].metric("Status", subscription.status.title())
status_cols[2].metric("Provider", subscription.provider.title())
status_cols[3].metric("Pro features", len(PRO_FEATURES if subscription.is_pro else FREE_FEATURES))

st.info("This demo entitlement layer does not charge money. It is ready to connect to a billing provider after checkout, webhook verification, customer records and server-side entitlement storage are configured.")

if not subscription.is_pro:
    st.subheader("⭐ Upgrade to Pro")
    if checkout_configured(st.secrets):
        checkout_url = st.secrets["BILLING_CHECKOUT_URL"]
        provider = st.secrets["BILLING_PROVIDER"]
        st.link_button(f"Continue to {provider} checkout", checkout_url, type="primary")
        st.caption("Payment is handled by the configured billing provider. The app should only receive verified subscription state from your backend/webhook.")
    else:
        st.warning("Billing checkout is not configured yet. No payment is requested by this page.")
        st.caption("Configure BILLING_PROVIDER and BILLING_CHECKOUT_URL only after your external billing checkout is ready.")

    if st.button("🧪 Preview Pro access", help="Development preview only; this does not create a paid subscription."):
        set_plan(st.session_state, "pro", status="trialing", provider="preview")
        st.rerun()
else:
    st.success("Your session currently has Pro entitlements.")
    if st.button("Return to Free preview"):
        set_plan(st.session_state, "free", status="active", provider="none")
        st.rerun()

st.divider()
st.subheader("🧩 Production billing architecture")
steps = [
    "Researcher signs in through the managed identity provider.",
    "Researcher starts checkout with the configured payment provider.",
    "Payment provider sends a signed webhook to your backend.",
    "Backend verifies the webhook and updates the researcher's subscription record.",
    "SciMantra reads the verified entitlement and gates Pro features server-side.",
    "Cancellation, renewal, failed payment and expiry events update the same record.",
]
for i, step in enumerate(steps, 1):
    st.write(f"**{i}.** {step}")

st.warning("Security: never store card numbers, CVV, passwords, payment secrets or provider signing secrets in Streamlit session state or source code. Use deployment secrets and server-side webhook verification.")
