from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from config import Config

app = Flask(__name__)  # create the application instance
app.config.from_object(Config)  # load config from this file

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from finerplan import routes, models
