import streamlit as st

from src.scimantra.subscription import FEATURES, FREE_FEATURES, PRO_FEATURES, checkout_configured, feature_label, get_subscription, set_plan
from src.scimantra.usage import usage_snapshot

st.set_page_config(page_title="SciMantra Plans", page_icon="💳", layout="wide")
st.title("💳 SciMantra Free vs Pro")
st.caption("Subscription, entitlements and daily usage overview.")
subscription = get_subscription(st.session_state)

with st.sidebar:
    st.header("Your plan")
    st.success("PRO" if subscription.is_pro else "FREE")
    st.caption(f"Status: {subscription.status}")

c1, c2 = st.columns(2)
with c1:
    st.subheader("🆓 Free")
    for feature in sorted(FREE_FEATURES): st.write(f"✅ {feature_label(feature)}")
    st.caption("Core research tools with daily usage limits.")
with c2:
    st.subheader("⭐ Pro")
    for feature in sorted(PRO_FEATURES): st.write(f"🚀 {feature_label(feature)}")
    st.caption("Full research workflow with unlimited application-layer usage.")

st.divider()
st.subheader("Feature access")
st.dataframe([{"Feature": label, "Free": "✅" if key in FREE_FEATURES else "—", "Pro": "✅"} for key, label in FEATURES.items()], width="stretch", hide_index=True)

st.subheader("📈 Today's usage")
for action, data in usage_snapshot(st.session_state).items():
    limit = "Unlimited" if data["limit"] is None else str(data["limit"])
    st.write(f"**{action.replace('_',' ').title()}** — {data['used']} / {limit}")
    if data["limit"] is not None: st.progress(min(data["used"] / max(data["limit"], 1), 1.0))

st.divider()
if not subscription.is_pro:
    st.subheader("⭐ Upgrade to Pro")
    try:
        from src.scimantra.billing import configured as stripe_configured, create_checkout_session
        stripe_ready = stripe_configured(st.secrets)
    except Exception:
        stripe_ready = False

    if stripe_ready:
        if st.button("💳 Subscribe to Pro", type="primary"):
            try:
                user = st.session_state.get("user") or st.session_state.get("supabase_user")
                user_id = str(getattr(user, "id", "")) if user else ""
                email = str(getattr(user, "email", "")) if user else ""
                if not user_id:
                    st.error("Please sign in to your SciMantra cloud account before subscribing.")
                else:
                    url = create_checkout_session(st.secrets, user_id, email)
                    st.link_button("Continue to secure checkout", url, type="primary")
            except Exception as exc:
                st.error(f"Could not start checkout: {exc}")
    elif checkout_configured(st.secrets):
        st.link_button(f"Continue to {st.secrets['BILLING_PROVIDER']} checkout", st.secrets["BILLING_CHECKOUT_URL"], type="primary")
    else:
        st.warning("Real payment checkout is not configured yet. No payment is requested by this page.")
        st.caption("Configure STRIPE_SECRET_KEY, STRIPE_PRICE_ID and APP_URL after creating your Stripe product/price.")

    if st.button("🧪 Preview Pro access", help="Development preview only; this does not create a paid subscription."):
        set_plan(st.session_state, "pro", status="trialing", provider="preview")
        st.rerun()
else:
    st.success("Pro entitlements are active for this session.")
    customer_id = subscription.customer_id
    if customer_id:
        try:
            from src.scimantra.billing import create_portal_session
            if st.button("⚙️ Manage subscription"):
                url = create_portal_session(st.secrets, customer_id)
                st.link_button("Open Stripe customer portal", url)
        except Exception:
            pass
    if st.button("Return to Free preview"):
        set_plan(st.session_state, "free", status="active", provider="none")
        st.rerun()

st.divider()
st.subheader("🧩 Production billing flow")
for i, step in enumerate(["Authenticated researcher starts checkout.", "Stripe processes payment details on its hosted checkout.", "Stripe sends a signed event to the trusted webhook service.", "Webhook verifies the signature and updates the subscription record.", "SciMantra reads verified entitlement and enforces Pro access.", "Renewal, cancellation, failed payment and expiry events update the same record."], 1):
    st.write(f"**{i}.** {step}")
st.warning("Never store card numbers, CVV, passwords, Stripe signing secrets or Supabase service-role keys in session state or source code. Production quota enforcement should be server-side.")
