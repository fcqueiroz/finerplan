import os
import sqlite3

from flask import current_app, g
from werkzeug.local import LocalProxy

APPLICATION_ROOT = os.path.abspath(os.path.dirname(__file__))


def _connect_to_database():
    database = current_app.config['SQLITE_DATABASE']
    return sqlite3.connect(database)


def _get_db():
    if 'db' not in g:
        g.db = _connect_to_database()
    return g.db


def _create_tables():
    """Create the database tables from schema."""
    schema = os.path.join(APPLICATION_ROOT, 'schema.sql')
    with open(schema, mode='r') as f:
        _get_db().executescript(f.read())



def create_database():
    """Create a database bounded to a Flask application context."""
    _create_tables()


def teardown_db(*args):
    """Close the database if it exists.

    Register this function as a Flask instance teardown_appcontext() handler
    to guarantee its execution, even if a before-request handler failed or
    was never executed.
    """
    _db = g.pop('db', None)
    if _db is not None:
        _db.close()


db = LocalProxy(_get_db)
