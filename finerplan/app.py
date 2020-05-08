"""Application setup."""
import sqlite3

from flask import Flask

from finerplan.config import obtain_config_object
from finerplan.database import db
from finerplan.frontend import dashboard_blueprint


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


def create_tables(flask_app: Flask, connection: sqlite3.Connection):
    """Create the database tables from schema."""
    with flask_app.open_resource('schema.sql', mode='r') as f:
        connection.executescript(f.read())


def init_database(flask_app: Flask):
    """Initialize database."""
    db.init_app(flask_app)
    with flask_app.app_context():
        # TODO:
        #  The db creation should be independent from app creation, but
        #  this line keeps the database creation automatic (expected behavior)
        create_tables(flask_app, db.connect())
