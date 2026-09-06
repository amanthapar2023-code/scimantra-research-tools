"""Centralized feature gating for SciMantra pages."""

from __future__ import annotations

import streamlit as st

from src.scimantra.subscription import feature_label, get_subscription


def subscription():
    return get_subscription(st.session_state)


def is_pro() -> bool:
    return subscription().is_pro


def allowed(feature: str) -> bool:
    return subscription().can_use(feature)


def require(feature: str) -> bool:
    """Show an upgrade prompt and return whether the current session is entitled."""
    if allowed(feature):
        return True
    st.warning(f"⭐ **{feature_label(feature)}** is a Pro feature.")
    st.info("Open **💳 SciMantra Plans** to review Pro access. The current demo does not charge money.")
    return False
