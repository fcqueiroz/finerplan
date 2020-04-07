import os
import sqlite3
import tempfile

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


def _create_database_file():
    """Manage temporary database files when SQLITE_DATABASE=''.

    Usage:
        Insert SQLITE_DATABASE='' into Flask instance config mapping to
        create a managed file-based temporary database.

    This function provides a complementary method for creating temporary
    databases that, different from the In-Memory options in sqlite lib,
    persists after the database connection is closed.

    Because this application adopts a connection-on-demand per request
    proposal, none of the provided In-Memory Databases suits the use case
    when one wants persistence while the application is running, but
    desires teardown between different application session (ie test conditions).

    Therefore, this method uses a system level call to create a temporary
    file that can be managed separately from database connections yielding
    significant control for testing scenarios that require clean,
    temporary and isolated databases.

    Ref:
    - https://flask.palletsprojects.com/en/1.1.x/appcontext/
    - https://flask.palletsprojects.com/en/1.1.x/patterns/sqlite3/
    - https://flask.palletsprojects.com/en/1.1.x/testing/
    - https://www.sqlite.org/inmemorydb.html
    """
    if current_app.config['SQLITE_DATABASE'] is '':
        handler, pathname = tempfile.mkstemp(suffix='.db', prefix='test.finerplan_')
        current_app.config.update(
            dict(SQLITE_DATABASE=pathname, SQLITE_DATABASE_HANDLER=handler)
        )


def create_database():
    """Create a database bounded to a Flask application context."""
    _create_database_file()  # Handle temporary databases
    _create_tables()


def destroy_database():
    """Remove the sqlite database file."""
    if current_app.config['ENV'] == 'production':
        print("WARN: Not allowed in production.")
        return

    os.close(current_app.config['SQLITE_DATABASE_HANDLER'])
    os.remove(current_app.config['SQLITE_DATABASE'])


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
