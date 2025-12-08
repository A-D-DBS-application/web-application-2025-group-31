from dotenv import load_dotenv
import os

# Laad .env zodat OPENAI_API_KEY beschikbaar is zodra Flask start
load_dotenv()

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config


db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Database initialiseren
    db.init_app(app)

    # Modellen importeren zodat SQLAlchemy ze registreert
    from app import models

    # Routes registreren (Blueprint)
    from app.routes import bp
    app.register_blueprint(bp)

    with app.app_context():
        db.create_all()

    return app


#Importeer de scheduler
from flask_apscheduler import APScheduler
from .routes import refresh_all_companies # Importeer de te plannen functie

# Definieer de scheduler
scheduler = APScheduler()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    
    # NIEUW: Voeg scheduler toe en start
    if app.config.get('SCHEDULER_ENABLED'):
        scheduler.init_app(app)
        # Registreer de taak
        scheduler.add_job(
            id='weekly_refresh', 
            func=refresh_all_companies, 
            trigger='interval', 
            weeks=1,
            # Start direct (of kies 'date' voor specifieke starttijd)
            start_date='2025-12-08 07:00:00', 
            name='Wekelijkse Data Refresh'
        )
        scheduler.start()


    # Registreer Blueprints
    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    return app
