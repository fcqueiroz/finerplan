from dotenv import load_dotenv
import pytest

from finerplan.app import create_app
from finerplan.database import db

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
        db.create_all()
        yield _app
        ctx.pop()
