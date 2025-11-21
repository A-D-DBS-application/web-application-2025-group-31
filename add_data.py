# add_data.py
# Doel: voorbeelddata toevoegen aan je Supabase-database

from app import create_app, db
from app.models import Company

# Maak de Flask-app aan via de factory
app = create_app()

with app.app_context():
    try:
        companies = [
            Company(
                name="Rival Technologies",
                website_url="https://rivaltech.com",
                headquarters="Amsterdam",
                team_size=45,
                funding=2000000
            ),
            Company(
                name="OpenAI",
                website_url="https://openai.com",
                headquarters="San Francisco",
                team_size=1000,
                funding=1100000000
            ),
            Company(
                name="TechNova",
                website_url="https://technova.io",
                headquarters="Rotterdam",
                team_size=120,
                funding=5000000
            )
        ]

        db.session.add_all(companies)
        db.session.commit()
        print("✅ Voorbeeldbedrijven toegevoegd aan Supabase!")

        count = db.session.execute(db.text("SELECT COUNT(*) FROM company")).scalar()
        print(f"📊 Aantal bedrijven in de database: {count}")

    except Exception as e:
        print("❌ Fout bij toevoegen van data:")
        print(e)


