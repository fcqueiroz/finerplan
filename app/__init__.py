from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import app_config
from app.routes import simple_page

# Globally accessible libraries
db = SQLAlchemy()
migrate = Migrate()


def create_app(config_name):
    """Initialize the core application"""
    _app = Flask(__name__)
    _app.config.from_object(app_config(config_name))

    # Initialize plugins
    db.init_app(_app)
    migrate.init_app(_app, db)

    with _app.app_context():
        # Include routes
        from . import routes

        # Register blueprints
        _app.register_blueprint(simple_page)

    return _app
