"""Sqlite Database bounded to a Flask application context."""
import sqlite3

from flask import g, current_app, Flask


def init_app(flaskapp: Flask):
    """Initializes the flask application."""
    flaskapp.teardown_appcontext(_teardown)


def connect() -> sqlite3.Connection:
    """Create or reuse an open connection to the database."""
    if 'db' not in g:
        database = current_app.config['SQLITE_DATABASE']
        g.db = sqlite3.connect(database)
    return g.db


def _teardown(*args):
    """Close the database if it exists."""
    _db = g.pop('db', None)
    if _db is not None:
        _db.close()
