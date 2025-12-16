class Config:
    SECRET_KEY = 'your_secret_key_here'
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres.wghuuwjgvqzcdtuzzwyl:Tamat312025.@aws-1-eu-central-1.pooler.supabase.com:5432/postgres'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # NIEUW: Scheduler instellingen
    SCHEDULER_API_ENABLED = False  # Houd de API uit, we hebben die niet nodig
    SCHEDULER_ENABLED = True  # Schakel de scheduler in


