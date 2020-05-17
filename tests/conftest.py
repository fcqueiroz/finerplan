from dotenv import load_dotenv
import pytest

from finerplan.app import create_app, create_tables
from finerplan import database as db

from tests import DataBaseFile

load_dotenv('.flaskenv')


@pytest.fixture()
def app():
    """Application Flask instance initialized for tests."""
    _app = create_app(environment='testing')
    with DataBaseFile() as tmp_file:
        _app.config['SQLITE_DATABASE'] = tmp_file
        ctx = _app.app_context()
        ctx.push()
        create_tables(_app, db.connect())
        yield _app
        ctx.pop()
