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
login.login_view = 'auth.login'


def create_app(config_name=None, script_info=None):
    """Initialize the core application"""
    app = Flask(__name__)
    app.config.from_object(app_config(config_name))

    init_plugins(app)

    # Register aditional commmands for flask.
    from finerplan.cli import register
    register(app)

    setup_logging(app)

    register_blueprints(app)

    return app


def init_plugins(app):
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)


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


def register_blueprints(app):
    with app.app_context():
        from finerplan.errors import bp as errors_bp
        app.register_blueprint(errors_bp)

        from finerplan.auth import bp as auth_bp
        app.register_blueprint(auth_bp)

        from finerplan.dashboard import bp as dashboard_bp
        app.register_blueprint(dashboard_bp)
