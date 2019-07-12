# 3rd Party Libraries
import pytest
# Local Imports
from app import create_app, db


@pytest.fixture(scope='session')
def app():
    app = create_app(config_name='testing')
    yield app


@pytest.fixture(scope='function')
def client(app):
    client = app.test_client()
    yield client


@pytest.fixture(scope='function')
def app_db(app):
    with app.app_context():
        db.create_all()
        yield db
        db.session.rollback()


class RoutingMixin(object):
    @staticmethod
    def check_200_status_code(response, url):
        assert 200 == response.status_code, f"wrong status code for '{url}'"

    @staticmethod
    def check_content_type(response, url):
        assert 'text/html' in response.content_type, f"wrong content type for '{url}'"