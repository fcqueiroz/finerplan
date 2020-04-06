"""Application setup."""
from flask import Flask

from finerplan.database import teardown_db
from finerplan.routes import dashboard_blueprint

from config import obtain_config_object


def load_config(flask_app: Flask, environment=None):
    """Load environment configuration into flask app instance."""
    if environment is None:
        environment = flask_app.config['ENV']

    flask_app.config.from_object(
        obtain_config_object(environment=environment)
    )


def create_app(**kwargs):
    """Initialize application instance."""
    _app = Flask(__name__)
    load_config(_app, **kwargs)
    register_blueprints(_app)
    init_database(_app)
    return _app


def register_blueprints(flask_app: Flask):
    """Register application views."""
    flask_app.register_blueprint(dashboard_blueprint)


def init_database(flask_app: Flask):
    """Initialize database."""
    with flask_app.app_context():
        flask_app.teardown_appcontext(teardown_db)
