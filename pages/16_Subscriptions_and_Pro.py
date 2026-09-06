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
    if checkout_configured(st.secrets):
        st.link_button(f"Continue to {st.secrets['BILLING_PROVIDER']} checkout", st.secrets["BILLING_CHECKOUT_URL"], type="primary")
    else:
        st.warning("Real payment checkout is not configured. No payment is requested by this page.")
        st.caption("Add BILLING_PROVIDER and BILLING_CHECKOUT_URL only after your external checkout and backend webhook are ready.")
    if st.button("🧪 Preview Pro access", help="Development preview only; this does not create a paid subscription."):
        set_plan(st.session_state, "pro", status="trialing", provider="preview")
        st.rerun()
else:
    st.success("Pro entitlements are active for this session.")
    if st.button("Return to Free preview"):
        set_plan(st.session_state, "free", status="active", provider="none")
        st.rerun()

st.divider()
st.subheader("🧩 Production billing flow")
for i, step in enumerate(["Authenticated researcher starts checkout.", "Billing provider processes payment.", "Provider sends a signed webhook to a trusted backend.", "Backend verifies the signature and updates subscriptions.", "App reads verified entitlement and enforces access.", "Renewal, cancellation, failure and expiry events update the same record."], 1):
    st.write(f"**{i}.** {step}")
st.warning("Never store card numbers, CVV, passwords, provider signing secrets or service-role keys in Streamlit session state or source code. Production quota enforcement should be server-side.")
