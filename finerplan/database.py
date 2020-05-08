import sqlite3

from flask import g, current_app, Flask


class SqliteDatabase(object):
    """Sqlite Database bounded to a Flask application context."""
    def __init__(self, flaskapp: Flask = None):
        self._app = flaskapp
        if flaskapp is not None:
            self.init_app(flaskapp)

    def init_app(self, flaskapp: Flask):
        """Initializes the flask application."""
        flaskapp.teardown_appcontext(self._teardown)

    @staticmethod
    def connect() -> sqlite3.Connection:
        """Create or reuse an open connection to the database."""
        if 'db' not in g:
            database = current_app.config['SQLITE_DATABASE']
            g.db = sqlite3.connect(database)
        return g.db

    @staticmethod
    def _teardown(*args):
        """Close the database if it exists."""
        _db = g.pop('db', None)
        if _db is not None:
            _db.close()


db = SqliteDatabase()
