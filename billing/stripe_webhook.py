"""Minimal Stripe webhook service.

Deploy this separately from Streamlit (Cloud Run, Render, Railway, etc.).
Required environment variables:
STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET, SUPABASE_URL,
SUPABASE_SERVICE_ROLE_KEY.

The service role key must NEVER be exposed to Streamlit users or committed.
"""
from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

import stripe
from supabase import create_client

stripe.api_key = os.environ["STRIPE_SECRET_KEY"]
supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])
WEBHOOK_SECRET = os.environ["STRIPE_WEBHOOK_SECRET"]


def _subscription_record(subscription, event_type: str):
    metadata = subscription.get("metadata") or {}
    user_id = metadata.get("supabase_user_id")
    if not user_id:
        return
    items = subscription.get("items", {}).get("data", [])
    price_id = items[0].get("price", {}).get("id", "") if items else ""
    period_end = subscription.get("current_period_end")
    period_end_iso = None
    if period_end:
        from datetime import datetime, timezone
        period_end_iso = datetime.fromtimestamp(period_end, tz=timezone.utc).isoformat()
    status = subscription.get("status", "active")
    plan = "pro" if status in {"active", "trialing"} else "free"
    payload = {
        "user_id": user_id,
        "plan": plan,
        "status": status,
        "provider": "stripe",
        "customer_id": subscription.get("customer", ""),
        "subscription_id": subscription.get("id", ""),
        "current_period_end": period_end_iso,
        "updated_at": "now()",
        "metadata": {"price_id": price_id, "event_type": event_type},
    }
    # Upsert is idempotent for repeated Stripe deliveries.
    supabase.table("subscriptions").upsert(payload, on_conflict="user_id").execute()


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length)
        signature = self.headers.get("Stripe-Signature", "")
        try:
            event = stripe.Webhook.construct_event(body, signature, WEBHOOK_SECRET)
            event_type = event["type"]
            obj = event["data"]["object"]
            if event_type in {"customer.subscription.created", "customer.subscription.updated", "customer.subscription.deleted"}:
                _subscription_record(obj, event_type)
            elif event_type == "checkout.session.completed":
                subscription_id = obj.get("subscription")
                if subscription_id:
                    sub = stripe.Subscription.retrieve(subscription_id)
                    # Carry the checkout metadata forward if Stripe did not copy it.
                    metadata = obj.get("metadata") or {}
                    if metadata.get("supabase_user_id") and not sub.get("metadata", {}).get("supabase_user_id"):
                        sub = stripe.Subscription.modify(subscription_id, metadata={"supabase_user_id": metadata["supabase_user_id"]})
                    _subscription_record(sub, event_type)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ok")
        except Exception as exc:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(str(exc).encode("utf-8")[:500])

    def log_message(self, fmt, *args):
        print(fmt % args)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
