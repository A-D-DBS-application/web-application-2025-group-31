import os
from dotenv import load_dotenv
from app import create_app

# API key geforceerd inladen uit .env bestand
load_dotenv(override=True)

app = create_app()

if __name__ == "__main__":
    # Luister op poort 5002 (zoals je had ingesteld)
    app.run(debug=True, port=5002)