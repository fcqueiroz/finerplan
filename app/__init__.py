from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import app_config


def create_app(config_name):
    _app = Flask(__name__)
    _app.config.from_object(app_config(config_name))
    with _app.app_context():
        db.init_app(_app)
        migrate.init_app(_app, db)

    return _app


db = SQLAlchemy()
migrate = Migrate()
app = create_app(config_name='development')
