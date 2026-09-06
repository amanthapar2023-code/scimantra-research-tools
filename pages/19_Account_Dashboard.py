import streamlit as st

from src.scimantra.subscription import FEATURES, feature_label, get_subscription
from src.scimantra.usage import usage_snapshot

st.set_page_config(page_title="SciMantra Account Dashboard", page_icon="📊", layout="wide")
st.title("📊 SciMantra Account Dashboard")
st.caption("Plan, usage and research-workspace overview.")

sub = get_subscription(st.session_state)

c1, c2, c3 = st.columns(3)
c1.metric("Plan", sub.plan.upper())
c2.metric("Subscription", sub.status.title())
c3.metric("Accessible features", len(FEATURES if sub.is_pro else [x for x in FEATURES if sub.can_use(x)]))

st.subheader("📈 Today's usage")
usage = usage_snapshot(st.session_state)
for action, data in usage.items():
    label = action.replace("_", " ").title()
    limit = "Unlimited" if data["limit"] is None else str(data["limit"])
    st.write(f"**{label}:** {data['used']} / {limit}")
    if data["limit"] is not None:
        st.progress(min(data["used"] / max(data["limit"], 1), 1.0))

st.divider()
st.subheader("⭐ Feature access")
rows = []
for key, label in FEATURES.items():
    rows.append((label, "PRO" if sub.is_pro or sub.can_use(key) and key not in {"basic_calculators", "basic_statistics", "data_analyzer", "project_manager"} else "FREE"))
for label, tier in rows:
    st.write(f"{'🚀' if tier == 'PRO' else '✅'} {label} — **{tier}**")

st.divider()
st.subheader("🚀 Research workflow")
for title, page in [
    ("👤 Login & Cloud Account", "17_Login_and_Cloud_Account"),
    ("☁️ Cloud Research Workspace", "18_Cloud_Project_Workspace"),
    ("💳 Plans & Pro", "16_Subscriptions_and_Pro"),
    ("📁 Research Project Manager", "14_Research_Project_Manager"),
]:
    st.write(f"• **{title}** — open it from the Streamlit navigation.")

st.info("Usage counters are currently session/day scoped. For production subscription enforcement across devices, persist usage in the cloud database and enforce Pro entitlements through a trusted backend.")
