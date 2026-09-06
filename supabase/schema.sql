-- SciMantra production data model for Supabase/PostgreSQL.
-- Run in the Supabase SQL editor after enabling the built-in Auth service.
-- This schema stores application metadata only; passwords remain in Supabase Auth.

create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  full_name text not null default '',
  institution text not null default '',
  avatar_url text not null default '',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.projects (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null references auth.users(id) on delete cascade,
  name text not null,
  status text not null default 'Planning',
  objective text not null default '',
  notes text not null default '',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.project_members (
  project_id uuid not null references public.projects(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  role text not null default 'viewer' check (role in ('owner','editor','viewer')),
  created_at timestamptz not null default now(),
  primary key (project_id, user_id)
);

create table if not exists public.datasets (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references public.projects(id) on delete cascade,
  owner_id uuid not null references auth.users(id) on delete cascade,
  name text not null,
  storage_path text not null default '',
  row_count integer not null default 0,
  column_count integer not null default 0,
  created_at timestamptz not null default now()
);

create table if not exists public.experiments (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references public.projects(id) on delete cascade,
  owner_id uuid not null references auth.users(id) on delete cascade,
  name text not null,
  design text not null default '',
  outcome text not null default '',
  status text not null default 'Planned',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.milestones (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references public.projects(id) on delete cascade,
  owner_id uuid not null references auth.users(id) on delete cascade,
  title text not null,
  due_date date,
  completed boolean not null default false,
  created_at timestamptz not null default now()
);

create table if not exists public.subscriptions (
  user_id uuid primary key references auth.users(id) on delete cascade,
  plan text not null default 'free' check (plan in ('free','pro')),
  status text not null default 'active',
  provider text not null default 'none',
  customer_id text not null default '',
  subscription_id text not null default '',
  current_period_end timestamptz,
  updated_at timestamptz not null default now()
);

create index if not exists projects_owner_idx on public.projects(owner_id);
create index if not exists datasets_project_idx on public.datasets(project_id);
create index if not exists experiments_project_idx on public.experiments(project_id);
create index if not exists milestones_project_idx on public.milestones(project_id);

alter table public.profiles enable row level security;
alter table public.projects enable row level security;
alter table public.project_members enable row level security;
alter table public.datasets enable row level security;
alter table public.experiments enable row level security;
alter table public.milestones enable row level security;
alter table public.subscriptions enable row level security;

-- Profiles: a user can read/update their own profile.
create policy if not exists "profiles_self_select" on public.profiles for select using (auth.uid() = id);
create policy if not exists "profiles_self_insert" on public.profiles for insert with check (auth.uid() = id);
create policy if not exists "profiles_self_update" on public.profiles for update using (auth.uid() = id) with check (auth.uid() = id);

-- Projects: owners have full access; project members can read and editors can modify.
create policy if not exists "projects_owner_all" on public.projects for all using (auth.uid() = owner_id) with check (auth.uid() = owner_id);
create policy if not exists "projects_member_select" on public.projects for select using (exists (select 1 from public.project_members m where m.project_id = id and m.user_id = auth.uid()));
create policy if not exists "projects_member_update" on public.projects for update using (exists (select 1 from public.project_members m where m.project_id = id and m.user_id = auth.uid() and m.role = 'editor'));

-- Membership rows are manageable by project owners.
create policy if not exists "members_owner_all" on public.project_members for all using (exists (select 1 from public.projects p where p.id = project_id and p.owner_id = auth.uid())) with check (exists (select 1 from public.projects p where p.id = project_id and p.owner_id = auth.uid()));
create policy if not exists "members_self_select" on public.project_members for select using (user_id = auth.uid());

-- Child records are visible to project owners/members. Owners/editors can modify.
create policy if not exists "datasets_project_access" on public.datasets for select using (exists (select 1 from public.projects p where p.id = project_id and (p.owner_id = auth.uid() or exists (select 1 from public.project_members m where m.project_id = p.id and m.user_id = auth.uid()))));
create policy if not exists "datasets_owner_insert" on public.datasets for insert with check (owner_id = auth.uid() and exists (select 1 from public.projects p where p.id = project_id and p.owner_id = auth.uid()));
create policy if not exists "experiments_project_access" on public.experiments for select using (exists (select 1 from public.projects p where p.id = project_id and (p.owner_id = auth.uid() or exists (select 1 from public.project_members m where m.project_id = p.id and m.user_id = auth.uid()))));
create policy if not exists "experiments_owner_insert" on public.experiments for insert with check (owner_id = auth.uid() and exists (select 1 from public.projects p where p.id = project_id and p.owner_id = auth.uid()));
create policy if not exists "milestones_project_access" on public.milestones for select using (exists (select 1 from public.projects p where p.id = project_id and (p.owner_id = auth.uid() or exists (select 1 from public.project_members m where m.project_id = p.id and m.user_id = auth.uid()))));
create policy if not exists "milestones_owner_insert" on public.milestones for insert with check (owner_id = auth.uid() and exists (select 1 from public.projects p where p.id = project_id and p.owner_id = auth.uid()));

-- A researcher can read their own subscription; billing updates should use a trusted backend/service role.
create policy if not exists "subscription_self_select" on public.subscriptions for select using (auth.uid() = user_id);

-- Automatically create profile + free subscription for new accounts.
create or replace function public.handle_new_user() returns trigger language plpgsql security definer set search_path = public as $$
begin
  insert into public.profiles (id, full_name) values (new.id, coalesce(new.raw_user_meta_data->>'full_name','')) on conflict (id) do nothing;
  insert into public.subscriptions (user_id, plan, status) values (new.id, 'free', 'active') on conflict (user_id) do nothing;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created after insert on auth.users for each row execute procedure public.handle_new_user();
