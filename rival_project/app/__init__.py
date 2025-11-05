from flask import Flask
from app.config import Config
from app.extensions import init_extensions

def create_app(config_class: type = Config):
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_object(config_class)

    # DB, migrations, etc.
    init_extensions(app)

    # Blueprints
    from app.blueprints.main import init_app as init_main
    init_main(app)
    from app.blueprints.auth import init_app as init_auth
    init_auth(app)
    from app.blueprints.api import init_app as init_api
    init_api(app)
    from app.blueprints.admin import init_app as init_admin
    init_admin(app)

    return app