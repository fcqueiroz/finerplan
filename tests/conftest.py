from dotenv import load_dotenv
import pytest

from finerplan.app import create_app
from finerplan.database import create_database

from tests import DataBaseFile

load_dotenv('.flaskenv')


@pytest.fixture(autouse=True)
def app():
    """Application Flask instance initialized for tests."""
    _app = create_app(environment='testing')
    with DataBaseFile() as tmp_file:
        _app.config['SQLITE_DATABASE'] = tmp_file
        ctx = _app.app_context()
        ctx.push()
        create_database()
        yield _app
        ctx.pop()
