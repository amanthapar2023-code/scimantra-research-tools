-- Optional production usage accounting. Run after schema.sql.
create table if not exists public.usage_daily (
  user_id uuid not null references auth.users(id) on delete cascade,
  usage_date date not null default current_date,
  dataset_uploads integer not null default 0,
  analysis_runs integer not null default 0,
  report_exports integer not null default 0,
  figure_exports integer not null default 0,
  ai_requests integer not null default 0,
  updated_at timestamptz not null default now(),
  primary key (user_id, usage_date)
);

alter table public.usage_daily enable row level security;
create policy if not exists "usage_self_select" on public.usage_daily for select using (auth.uid() = user_id);
-- Writes should be performed by a trusted backend/service role to prevent quota bypass.
