"""
Merge legacy 'companies' table into canonical 'company' without data loss.

This script:
1) Checks if 'companies' exists.
2) If empty: drops it (CASCADE) and exits.
3) If not empty: creates a backup copy 'companies_backup',
   copies non-duplicate rows into 'company' (matches by lower(name) or URL),
   then drops 'companies' with CASCADE.

Run once from the project root venv after configuring DB:
    python rival_project/scripts/merge_company_tables.py
"""

from sqlalchemy import text
from app import create_app
from app.extensions import db


def to_regclass_exists(engine, fqname: str) -> bool:
    sql = text("select to_regclass(:n)")
    res = engine.execute(sql, {"n": fqname}).scalar()
    return res is not None


def main():
    app = create_app()
    with app.app_context():
        engine = db.engine

        # Detect table existence (try with and without public schema)
        if not (to_regclass_exists(engine, 'public.companies') or to_regclass_exists(engine, 'companies')):
            print("No 'companies' table found. Nothing to merge.")
            return

        # Count rows in legacy table
        try:
            count = engine.execute(text('select count(*) from companies')).scalar()
        except Exception:
            # If schema-qualified is needed
            count = engine.execute(text('select count(*) from public.companies')).scalar()

        if count == 0:
            # Safe drop when empty
            print("'companies' table is empty. Dropping it…")
            engine.execute(text('drop table if exists companies cascade'))
            return

        print(f"Found {count} rows in 'companies'. Creating backup and merging into 'company'…")

        # Create backup if not exists
        engine.execute(text('create table if not exists companies_backup as table companies with data'))

        # Ensure canonical table exists
        # If it doesn't, we can't proceed safely via this script.
        if not (to_regclass_exists(engine, 'public.company') or to_regclass_exists(engine, 'company')):
            raise RuntimeError("Canonical table 'company' does not exist. Aborting to avoid data loss.")

        # Insert non-duplicate rows based on name or URL match (case-insensitive)
        insert_sql = text(
            """
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
            """
        )
        engine.execute(insert_sql)

        # Finally drop legacy table
        engine.execute(text('drop table companies cascade'))
        print("Merge complete. 'companies' dropped. Backup kept as 'companies_backup'.")


if __name__ == "__main__":
    main()
