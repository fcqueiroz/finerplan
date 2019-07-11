# 3rd Party Libraries
import pytest
# Local Imports
from app import create_app, db as _db


@pytest.fixture()
def app():
    app = create_app(config_name='testing')
    yield app


@pytest.fixture()
def client(app):
    client = app.test_client()
    yield client


@pytest.fixture()
def db(app):
    db = _db
    with app.app_context():
        db.create_all()
        yield db
