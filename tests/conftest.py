# 3rd Party Libraries
import pytest
# Local Imports
from app import create_app


@pytest.fixture()
def app():
    app = create_app(config_name='testing')
    yield app


@pytest.fixture()
def client(app):
    client = app.test_client()
    yield client
