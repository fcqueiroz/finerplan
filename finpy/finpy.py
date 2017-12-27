import os
import sqlite3
from flask import Flask, g

app = Flask(__name__) # create the application instance
app.config.from_object(__name__) # load config from this file

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE = os.path.join(app.root_path, 'finpy.db'),
    SECRET_KEY = (os.environ.get('SECRET_KEY') or 'you-will-never-guess'),
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def initdb():
    """Initializes the database."""
    



import finpy.routes
