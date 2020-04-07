from dotenv import load_dotenv
import pytest

from finerplan.app import create_app
from finerplan.database import create_database, destroy_database

load_dotenv('.flaskenv')


@pytest.fixture(autouse=True)
def app():
    """Application Flask instance initialized for tests."""
    _app = create_app(environment='testing')
    ctx = _app.app_context()
    ctx.push()
    create_database()
    yield _app
    destroy_database()
    ctx.pop()
