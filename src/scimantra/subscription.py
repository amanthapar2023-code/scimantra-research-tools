"""Subscription and entitlement helpers for SciMantra.

This module is intentionally provider-neutral. It can be connected later to
Stripe, Razorpay, Paddle, or another billing provider without changing the
research-tool pages. It never stores card details, passwords, or API keys.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

FREE_PLAN = "free"
PRO_PLAN = "pro"

FEATURES: dict[str, str] = {
    "basic_calculators": "Basic laboratory calculators",
    "basic_statistics": "Basic statistics",
    "data_analyzer": "Data analyzer",
    "advanced_analysis": "Advanced experimental analysis",
    "publication_figures": "Publication figure generator",
    "automated_reports": "Automated research reports",
    "power_analysis": "Experimental design & power analysis",
    "project_manager": "Research project manager",
    "ai_assistant": "AI research assistant",
    "statistical_copilot": "Statistical Copilot",
    "pro_workspace": "Pro research workspace",
    "cloud_projects": "Cloud project persistence",
}

FREE_FEATURES = {
    "basic_calculators",
    "basic_statistics",
    "data_analyzer",
    "project_manager",
}

PRO_FEATURES = set(FEATURES)


@dataclass
class Subscription:
    plan: str = FREE_PLAN
    status: str = "active"
    provider: str = "none"
    customer_id: str = ""
    subscription_id: str = ""
    current_period_end: str = ""
    features: set[str] = field(default_factory=set)
    updated_at: str = ""

    def __post_init__(self) -> None:
        self.plan = self.plan if self.plan in {FREE_PLAN, PRO_PLAN} else FREE_PLAN
        self.status = self.status or "active"
        if not self.features:
            self.features = set(PRO_FEATURES if self.plan == PRO_PLAN else FREE_FEATURES)
        if not self.updated_at:
            self.updated_at = datetime.now(timezone.utc).isoformat()

    @property
    def is_pro(self) -> bool:
        return self.plan == PRO_PLAN and self.status in {"active", "trialing"}

    def can_use(self, feature: str) -> bool:
        return feature in (PRO_FEATURES if self.is_pro else FREE_FEATURES)

    def as_dict(self) -> dict[str, Any]:
        return {
            "plan": self.plan,
            "status": self.status,
            "provider": self.provider,
            "customer_id": self.customer_id,
            "subscription_id": self.subscription_id,
            "current_period_end": self.current_period_end,
            "features": sorted(self.features),
            "updated_at": self.updated_at,
        }


def get_subscription(state: dict[str, Any]) -> Subscription:
    raw = state.get("subscription")
    if isinstance(raw, Subscription):
        return raw
    if isinstance(raw, dict):
        return Subscription(
            plan=raw.get("plan", FREE_PLAN),
            status=raw.get("status", "active"),
            provider=raw.get("provider", "none"),
            customer_id=raw.get("customer_id", ""),
            subscription_id=raw.get("subscription_id", ""),
            current_period_end=raw.get("current_period_end", ""),
            features=set(raw.get("features", [])),
            updated_at=raw.get("updated_at", ""),
        )
    subscription = Subscription()
    state["subscription"] = subscription
    return subscription


def set_plan(state: dict[str, Any], plan: str, *, status: str = "active", provider: str = "none") -> Subscription:
    subscription = Subscription(plan=plan, status=status, provider=provider)
    state["subscription"] = subscription
    return subscription


def feature_label(feature: str) -> str:
    return FEATURES.get(feature, feature.replace("_", " ").title())


def checkout_configured(secrets: Any) -> bool:
    """Return whether a future billing provider has been configured.

    The app deliberately does not process payments itself. A production
    provider should verify webhooks server-side and then update entitlements.
    """
    try:
        return bool(secrets.get("BILLING_PROVIDER")) and bool(secrets.get("BILLING_CHECKOUT_URL"))
    except Exception:
        return False
