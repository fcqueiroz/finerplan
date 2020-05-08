import sqlite3

from flask import g, current_app, Flask


class SqliteDatabase(object):
    """Control a Sqlite Database bounded to a Flask application context."""
    def __init__(self, flaskapp: Flask = None):
        self._app = flaskapp
        if flaskapp is not None:
            self.init_app(flaskapp)

    def init_app(self, flaskapp: Flask):
        """Initializes the flask application."""
        flaskapp.teardown_appcontext(self.teardown_db)

    @staticmethod
    def connect():
        """Open a connection to the database storage."""
        if 'db' not in g:
            database = current_app.config['SQLITE_DATABASE']
            g.db = sqlite3.connect(database)
        return g.db

    @staticmethod
    def teardown_db(*args):
        """Close the database if it exists.

        Register this function as a Flask instance teardown_appcontext()
        handler to guarantee its execution, even if a before-request
        handler failed or was never executed.
        """
        _db = g.pop('db', None)
        if _db is not None:
            _db.close()


db = SqliteDatabase()
