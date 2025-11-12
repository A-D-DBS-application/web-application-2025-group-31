-- Consolidate to canonical 'company' table and clean empty duplicates
-- Run this in Supabase SQL editor or psql against your database.

begin;

-- 1) If 'companies' exists and has data that isn't already in 'company', merge it
-- Matching heuristic: case-insensitive name or exact URL match
create table if not exists company_backup_merge as table company with data;

do $$
begin
  if to_regclass('public.companies') is not null then
    -- Insert non-duplicates into company
    insert into company (name, website_url, headquarters, created_at)
    select t.name,
           t.url as website_url,
           t.location as headquarters,
           coalesce(t.created_at, now())
    from companies t
    left join company c
      on lower(c.name) = lower(t.name)
      or (
        c.website_url is not null and t.url is not null
        and lower(c.website_url) = lower(t.url)
      )
    where c.company_id is null;
  end if;
end$$;

-- 2) If 'companies' is empty after merge, drop it
do $$
begin
  if to_regclass('public.companies') is not null then
    if (select count(*) from companies) = 0 then
      drop table companies cascade;
    end if;
  end if;
end$$;

-- 3) Update dependent FKs to reference company(company_id) and types to bigint
-- Watchlist
do $$
begin
  if to_regclass('public.watchlist') is not null then
    -- Relax constraints if present and retarget
    begin
      alter table watchlist drop constraint if exists watchlist_company_id_fkey;
    exception when undefined_object then null; end;

    alter table watchlist
      alter column company_id type bigint using company_id::bigint,
      alter column company_id set not null;

    alter table watchlist
      add constraint watchlist_company_id_fkey
      foreign key (company_id) references company(company_id) on delete cascade;
  end if;
end$$;

-- Company finance
do $$
begin
  if to_regclass('public.company_finance') is not null then
    begin
      alter table company_finance drop constraint if exists company_finance_company_id_fkey;
    exception when undefined_object then null; end;

    alter table company_finance
      alter column company_id type bigint using company_id::bigint,
      alter column company_id set not null;

    alter table company_finance
      add constraint company_finance_company_id_fkey
      foreign key (company_id) references company(company_id) on delete cascade;
  end if;
end$$;

commit;