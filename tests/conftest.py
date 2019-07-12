# 3rd Party Libraries
import pytest
# Local Imports
from app import create_app, db


@pytest.fixture(scope='session')
def app():
    app = create_app(config_name='testing')
    yield app


@pytest.fixture(scope='module')
def client(app):
    client = app.test_client()
    yield client


@pytest.fixture(scope='function')
def app_db(app):
    with app.app_context():
        db.create_all()
        yield db
        db.session.rollback()
