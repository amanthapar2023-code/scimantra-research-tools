-- SciMantra production data model for Supabase/PostgreSQL.
-- Run in the Supabase SQL editor. Passwords remain in Supabase Auth.

create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  full_name text not null default '', institution text not null default '', avatar_url text not null default '',
  created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
create table if not exists public.projects (
  id uuid primary key default gen_random_uuid(), owner_id uuid not null references auth.users(id) on delete cascade,
  name text not null, status text not null default 'Planning', objective text not null default '', notes text not null default '',
  created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
create table if not exists public.project_members (
  project_id uuid not null references public.projects(id) on delete cascade, user_id uuid not null references auth.users(id) on delete cascade,
  role text not null default 'viewer' check (role in ('owner','editor','viewer')), created_at timestamptz not null default now(), primary key (project_id,user_id)
);
create table if not exists public.datasets (
  id uuid primary key default gen_random_uuid(), project_id uuid not null references public.projects(id) on delete cascade,
  owner_id uuid not null references auth.users(id) on delete cascade, name text not null, storage_path text not null default '',
  row_count integer not null default 0, column_count integer not null default 0, created_at timestamptz not null default now()
);
create table if not exists public.experiments (
  id uuid primary key default gen_random_uuid(), project_id uuid not null references public.projects(id) on delete cascade,
  owner_id uuid not null references auth.users(id) on delete cascade, name text not null, design text not null default '', outcome text not null default '',
  status text not null default 'Planned', created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
create table if not exists public.milestones (
  id uuid primary key default gen_random_uuid(), project_id uuid not null references public.projects(id) on delete cascade,
  owner_id uuid not null references auth.users(id) on delete cascade, title text not null, due_date date, completed boolean not null default false, created_at timestamptz not null default now()
);
create table if not exists public.subscriptions (
  user_id uuid primary key references auth.users(id) on delete cascade, plan text not null default 'free' check (plan in ('free','pro')),
  status text not null default 'active', provider text not null default 'none', customer_id text not null default '', subscription_id text not null default '',
  current_period_end timestamptz, updated_at timestamptz not null default now()
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

create or replace function public.is_project_member(p_project_id uuid) returns boolean language sql security definer set search_path = public stable as $$
  select exists (select 1 from public.project_members m where m.project_id = p_project_id and m.user_id = auth.uid());
$$;
create or replace function public.is_project_editor(p_project_id uuid) returns boolean language sql security definer set search_path = public stable as $$
  select exists (select 1 from public.project_members m where m.project_id = p_project_id and m.user_id = auth.uid() and m.role in ('owner','editor'));
$$;
revoke all on function public.is_project_member(uuid) from public;
revoke all on function public.is_project_editor(uuid) from public;
grant execute on function public.is_project_member(uuid) to authenticated;
grant execute on function public.is_project_editor(uuid) to authenticated;

drop policy if exists profiles_self_select on public.profiles;
drop policy if exists profiles_self_insert on public.profiles;
drop policy if exists profiles_self_update on public.profiles;
create policy profiles_self_select on public.profiles for select using (auth.uid() = id);
create policy profiles_self_insert on public.profiles for insert with check (auth.uid() = id);
create policy profiles_self_update on public.profiles for update using (auth.uid() = id) with check (auth.uid() = id);

drop policy if exists projects_owner_all on public.projects;
drop policy if exists projects_member_select on public.projects;
drop policy if exists projects_member_update on public.projects;
create policy projects_owner_all on public.projects for all using (auth.uid() = owner_id) with check (auth.uid() = owner_id);
create policy projects_member_select on public.projects for select using (public.is_project_member(id));
create policy projects_member_update on public.projects for update using (public.is_project_editor(id));

drop policy if exists members_owner_all on public.project_members;
drop policy if exists members_self_select on public.project_members;
create policy members_owner_all on public.project_members for all using (exists (select 1 from public.projects p where p.id = project_id and p.owner_id = auth.uid())) with check (exists (select 1 from public.projects p where p.id = project_id and p.owner_id = auth.uid()));
create policy members_self_select on public.project_members for select using (user_id = auth.uid());

drop policy if exists datasets_project_access on public.datasets;
drop policy if exists datasets_owner_insert on public.datasets;
drop policy if exists datasets_owner_update on public.datasets;
drop policy if exists datasets_owner_delete on public.datasets;
create policy datasets_project_access on public.datasets for select using (exists (select 1 from public.projects p where p.id = project_id and (p.owner_id = auth.uid() or public.is_project_member(p.id))));
create policy datasets_owner_insert on public.datasets for insert with check (owner_id = auth.uid() and public.is_project_editor(project_id));
create policy datasets_owner_update on public.datasets for update using (owner_id = auth.uid() and public.is_project_editor(project_id)) with check (owner_id = auth.uid());
create policy datasets_owner_delete on public.datasets for delete using (owner_id = auth.uid() and public.is_project_editor(project_id));

drop policy if exists experiments_project_access on public.experiments;
drop policy if exists experiments_owner_insert on public.experiments;
drop policy if exists experiments_owner_update on public.experiments;
drop policy if exists experiments_owner_delete on public.experiments;
create policy experiments_project_access on public.experiments for select using (exists (select 1 from public.projects p where p.id = project_id and (p.owner_id = auth.uid() or public.is_project_member(p.id))));
create policy experiments_owner_insert on public.experiments for insert with check (owner_id = auth.uid() and public.is_project_editor(project_id));
create policy experiments_owner_update on public.experiments for update using (owner_id = auth.uid() and public.is_project_editor(project_id));
create policy experiments_owner_delete on public.experiments for delete using (owner_id = auth.uid() and public.is_project_editor(project_id));

drop policy if exists milestones_project_access on public.milestones;
drop policy if exists milestones_owner_insert on public.milestones;
drop policy if exists milestones_owner_update on public.milestones;
drop policy if exists milestones_owner_delete on public.milestones;
create policy milestones_project_access on public.milestones for select using (exists (select 1 from public.projects p where p.id = project_id and (p.owner_id = auth.uid() or public.is_project_member(p.id))));
create policy milestones_owner_insert on public.milestones for insert with check (owner_id = auth.uid() and public.is_project_editor(project_id));
create policy milestones_owner_update on public.milestones for update using (owner_id = auth.uid() and public.is_project_editor(project_id));
create policy milestones_owner_delete on public.milestones for delete using (owner_id = auth.uid() and public.is_project_editor(project_id));

drop policy if exists subscription_self_select on public.subscriptions;
create policy subscription_self_select on public.subscriptions for select using (auth.uid() = user_id);

-- Every new cloud project automatically gives its creator an owner membership.
create or replace function public.handle_new_project() returns trigger language plpgsql security definer set search_path = public as $$
begin
  insert into public.project_members (project_id, user_id, role) values (new.id, new.owner_id, 'owner') on conflict (project_id, user_id) do update set role = 'owner';
  return new;
end;
$$;
drop trigger if exists on_project_created on public.projects;
create trigger on_project_created after insert on public.projects for each row execute procedure public.handle_new_project();

create or replace function public.touch_project_updated_at() returns trigger language plpgsql security definer set search_path = public as $$
begin
  new.updated_at = now();
  return new;
end;
$$;
drop trigger if exists projects_touch_updated_at on public.projects;
create trigger projects_touch_updated_at before update on public.projects for each row execute procedure public.touch_project_updated_at();

create or replace function public.handle_new_user() returns trigger language plpgsql security definer set search_path = public as $$
begin
  insert into public.profiles (id, full_name) values (new.id, coalesce(new.raw_user_meta_data->>'full_name','')) on conflict (id) do nothing;
  insert into public.subscriptions (user_id, plan, status) values (new.id, 'free', 'active') on conflict (user_id) do nothing;
  return new;
end;
$$;
drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created after insert on auth.users for each row execute procedure public.handle_new_user();
