# SciMantra Cloud Setup

This directory contains the production database schema for the optional cloud account layer.

## 1. Create a Supabase project

Create a project in Supabase and enable the authentication methods you want to offer. Email/password is supported by the SciMantra account page.

## 2. Apply the schema

Open the Supabase SQL editor and run `supabase/schema.sql`.

The schema creates:

- `profiles`
- `projects`
- `project_members`
- `datasets`
- `experiments`
- `milestones`
- `subscriptions`

Row Level Security policies restrict application reads/writes by authenticated user and project membership.

## 3. Configure Streamlit secrets

Add the Supabase project URL and publishable/anon key to the deployment secrets:

```toml
SUPABASE_URL = "https://YOUR_PROJECT.supabase.co"
SUPABASE_ANON_KEY = "YOUR_PUBLISHABLE_OR_ANON_KEY"
```

Install the optional client dependency by adding `supabase` to `requirements.txt` when you are ready to enable cloud accounts.

## 4. Billing

The application has a provider-neutral subscription model. Configure checkout only after selecting a payment provider.

For a production billing system:

1. User starts checkout.
2. Provider processes payment.
3. Provider sends a signed webhook to a trusted backend.
4. Backend verifies the signature.
5. Backend updates `public.subscriptions` using a privileged server-side credential.
6. The Streamlit app reads the verified subscription state and gates Pro features.

Never expose a service-role key, webhook signing secret, payment credentials or card data to the Streamlit browser/session.

## 5. Current limitation

The repository now contains the application layer and production database design, but it does **not** claim that cloud authentication or real payment processing is live until the external Supabase/billing accounts and deployment secrets are configured.
