# SciMantra production billing/admin setup

## 1. Supabase

Apply `supabase/schema.sql` and then `supabase/usage.sql` in the Supabase SQL editor.

Create the Streamlit secrets:

- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SCIMANTRA_ADMIN_EMAILS` — comma-separated administrator emails

The Supabase service-role key must stay on a trusted backend only; never put it in GitHub source code.

## 2. Stripe

Create a recurring Pro product and price in Stripe. Put the resulting price ID in the Streamlit secret `STRIPE_PRICE_ID` and the server-side secret key in `STRIPE_SECRET_KEY`.

Configure the application URL as `APP_URL`.

## 3. Webhook

Deploy `billing/stripe_webhook.py` separately from Streamlit. Configure:

- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`

Register the webhook for checkout completion and subscription lifecycle events.

## 4. Security

Use HTTPS, MFA for administrators, least-privilege access, secret storage, and webhook signature verification. Never accept a client-provided `plan=pro` value as proof of payment.

The Streamlit admin page is deliberately read-mostly. Billing changes should originate from the verified provider webhook.
