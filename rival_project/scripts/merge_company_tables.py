"""
Merge legacy 'company' table into canonical 'companies' without data loss.

This script:
1) Checks if 'company' exists.
2) If empty: drops it (CASCADE) and exits.
3) If not empty: creates a backup copy 'company_backup',
   copies non-duplicate rows into 'companies' (matches by lower(name) or URL),
   then drops 'company' with CASCADE.

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
        if not (to_regclass_exists(engine, 'public.company') or to_regclass_exists(engine, 'company')):
            print("No 'company' table found. Nothing to merge.")
            return

        # Count rows in legacy table
        try:
            count = engine.execute(text('select count(*) from company')).scalar()
        except Exception:
            # If schema-qualified is needed
            count = engine.execute(text('select count(*) from public.company')).scalar()

        if count == 0:
            # Safe drop when empty
            print("'company' table is empty. Dropping it…")
            engine.execute(text('drop table if exists company cascade'))
            return

        print(f"Found {count} rows in 'company'. Creating backup and merging into 'companies'…")

        # Create backup if not exists
        engine.execute(text('create table if not exists company_backup as table company with data'))

        # Ensure canonical table exists
        # If it doesn't, we can't proceed safely via this script.
        if not (to_regclass_exists(engine, 'public.companies') or to_regclass_exists(engine, 'companies')):
            raise RuntimeError("Canonical table 'companies' does not exist. Aborting to avoid data loss.")

        # Insert non-duplicate rows based on name or URL match (case-insensitive)
        insert_sql = text(
            """
            insert into companies (name, url, location, created_at)
            select c.name,
                   c.website_url as url,
                   c.headquarters as location,
                   coalesce(c.created_at, now())
            from company c
            left join companies t
              on lower(t.name) = lower(c.name)
              or (
                 t.url is not null and c.website_url is not null
                 and lower(t.url) = lower(c.website_url)
              )
            where t.id is null;
            """
        )
        engine.execute(insert_sql)

        # Finally drop legacy table
        engine.execute(text('drop table company cascade'))
        print("Merge complete. 'company' dropped. Backup kept as 'company_backup'.")


if __name__ == "__main__":
    main()
