-- =========================================================
-- Database schema
-- Generated from Supabase
-- For documentation purposes only
-- =========================================================

create table public.app_user (
  user_id bigserial not null,
  username text not null,
  email text not null,
  password_hash text not null,
  created_at timestamp with time zone null default now(),
  digest_frequency text null default 'weekly'::text,
  digest_signals jsonb null default '[]'::jsonb,
  constraint app_user_pkey primary key (user_id),
  constraint app_user_email_key unique (email),
  constraint app_user_username_key unique (username)
) TABLESPACE pg_default;

create table public.audit_log (
  log_id bigserial not null,
  source_name text null,
  source_url text null,
  retrieved_at timestamp with time zone null default now(),
  company_id bigint null,
  constraint audit_log_pkey primary key (log_id),
  constraint audit_log_company_id_fkey foreign KEY (company_id) references company (company_id) on delete CASCADE
) TABLESPACE pg_default;

create table public.change_event (
  event_id bigserial not null,
  event_type text null,
  description text null,
  detected_at timestamp with time zone null default now(),
  company_id bigint null,
  constraint change_event_pkey primary key (event_id),
  constraint change_event_company_id_fkey foreign KEY (company_id) references company (company_id) on delete CASCADE
) TABLESPACE pg_default;

create table public.company (
  company_id bigserial not null,
  name text not null,
  website_url text null,
  headquarters text null,
  team_size integer null,
  funding text null,
  office_locations text null,
  traction_signals text null,
  funding_history text null,
  ai_summary text null,
  value_proposition text null,
  product_description text null,
  target_segment text null,
  pricing text null,
  key_features jsonb null,
  competitors jsonb null,
  created_at timestamp with time zone null default now(),
  sector_id integer null,
  constraint company_pkey primary key (company_id),
  constraint fk_sector foreign KEY (sector_id) references sectors (sector_id)
) TABLESPACE pg_default;

create table public.metric (
  metric_id bigserial not null,
  company_id bigint null,
  name text not null,
  description text null,
  tracking_frequency text null,
  value numeric null,
  active boolean null default true,
  last_updated timestamp with time zone null default now(),
  constraint metric_pkey primary key (metric_id),
  constraint metric_company_id_fkey foreign KEY (company_id) references company (company_id) on delete CASCADE
) TABLESPACE pg_default;

create table public.metric_history (
  id bigserial not null,
  company_id bigint not null,
  name text not null,
  value numeric null,
  recorded_at timestamp with time zone null default now(),
  source text null,
  constraint metric_history_pkey primary key (id),
  constraint metric_history_company_id_fkey foreign KEY (company_id) references company (company_id) on delete CASCADE
) TABLESPACE pg_default;

create index IF not exists ix_metric_history_recorded_at on public.metric_history using btree (recorded_at) TABLESPACE pg_default;

create table public.sectors (
  sector_id integer not null default nextval('sectors_sector_id_seq'::regclass),
  name character varying(100) not null,
  constraint sectors_pkey primary key (sector_id),
  constraint sectors_name_key unique (name)
) TABLESPACE pg_default;