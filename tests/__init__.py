import os
import tempfile


class DataBaseFile(object):
    """Create a temporary file for sqlite database.

    This provides a complementary method for creating temporary
    databases that, different from the Sqlite in-memory options,
    persists after the database connection is closed.

    Because the Flask application opens and closes the connection per
    each request, none of the Sqlite standard options for temporary
    database permits to keep the database alive during the whole
    application lifecycle, which affect test conditions.

    Therefore, this class uses a system level call to create a temporary
    file that can be managed separately from database connections and
    Flask application context yielding significant control for testing
    scenarios that require clean, temporary and isolated databases.

    Ref:
    - https://flask.palletsprojects.com/en/1.1.x/appcontext/
    - https://flask.palletsprojects.com/en/1.1.x/patterns/sqlite3/
    - https://flask.palletsprojects.com/en/1.1.x/testing/
    - https://www.sqlite.org/inmemorydb.html
    """
    def __init__(self, prefix='test.finerplan_', suffix='.db'):
        self.prefix = prefix
        self.suffix = suffix

    def __enter__(self):
        fd, fullpath = tempfile.mkstemp(prefix=self.prefix, suffix=self.suffix)
        # The file descriptor must be closed to avoid leaks
        # https://www.logilab.org/blogentry/17873
        os.close(fd)

        self._path = fullpath
        return fullpath

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.remove(self._path)
