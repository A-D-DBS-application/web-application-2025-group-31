import os 

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # NIEUW: Scheduler instellingen
    SCHEDULER_API_ENABLED = False  # Houd de API uit, we hebben die niet nodig
    SCHEDULER_ENABLED = True  # Schakel de scheduler in


