"""Server-side Stripe helpers.

Required Streamlit secrets:
STRIPE_SECRET_KEY, STRIPE_PRICE_ID, APP_URL

The secret key is used only on the server. Payment status must come from the
verified webhook/backend, never from client input.
"""
from __future__ import annotations

from typing import Any


def _stripe(secrets: Any):
    import stripe
    key = secrets.get("STRIPE_SECRET_KEY")
    if not key:
        raise RuntimeError("STRIPE_SECRET_KEY is not configured")
    stripe.api_key = key
    return stripe


def configured(secrets: Any) -> bool:
    try:
        return bool(secrets.get("STRIPE_SECRET_KEY")) and bool(secrets.get("STRIPE_PRICE_ID")) and bool(secrets.get("APP_URL"))
    except Exception:
        return False


def create_checkout_session(secrets: Any, user_id: str, email: str = "") -> str:
    stripe = _stripe(secrets)
    app_url = str(secrets["APP_URL"]).rstrip("/")
    params = {
        "mode": "subscription",
        "line_items": [{"price": secrets["STRIPE_PRICE_ID"], "quantity": 1}],
        "success_url": f"{app_url}/?billing=success",
        "cancel_url": f"{app_url}/?billing=cancelled",
        "client_reference_id": user_id,
        "metadata": {"supabase_user_id": user_id},
    }
    if email:
        params["customer_email"] = email
    session = stripe.checkout.Session.create(**params)
    return str(session.url)


def create_portal_session(secrets: Any, customer_id: str) -> str:
    stripe = _stripe(secrets)
    app_url = str(secrets["APP_URL"]).rstrip("/")
    session = stripe.billing_portal.Session.create(customer=customer_id, return_url=f"{app_url}/")
    return str(session.url)
