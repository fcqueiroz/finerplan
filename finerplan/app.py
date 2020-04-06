"""Application setup."""
from flask import Flask

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
    return _app


app = create_app()

from finerplan.sql import create_tables

create_tables(database=app.config['DATABASE'])

def register_blueprints(flask_app: Flask):
    """Register application views."""
    flask_app.register_blueprint(dashboard_blueprint)
