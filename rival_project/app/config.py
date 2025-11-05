class Config:
    SECRET_KEY = 'supersecretkey'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'