import logging
from logging.handlers import RotatingFileHandler
import os

from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import app_config

# Globally accessible libraries
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'simple_page.login'


def create_app(config_name):
    """Initialize the core application"""
    _app = Flask(__name__)
    _app.config.from_object(app_config(config_name))

    # Initialize plugins
    db.init_app(_app)
    migrate.init_app(_app, db)
    login.init_app(_app)

    setup_logging(_app)

    with _app.app_context():
        # Include routes
        from . import routes, error_handlers

        # Register blueprints
        _app.register_blueprint(routes.simple_page)
        _app.register_blueprint(error_handlers.blueprint)

    return _app


def setup_logging(app):
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/finerplan.log', maxBytes=10240,
                                           backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Finerplan startup')
