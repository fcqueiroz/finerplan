# 3rd Party Libraries
import pytest
# Local Imports
from app import create_app, db
from app.models import User, Transaction


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
        db.drop_all()


class RoutingMixin(object):
    @staticmethod
    def check_200_status_code(response, url):
        assert 200 == response.status_code, f"wrong status code for '{url}'"

    @staticmethod
    def check_content_type(response, url):
        assert 'text/html' in response.content_type, f"wrong content type for '{url}'"


class DatabaseMixin(object):
    test_user = {
        'username': 'tester',
        'email': 'tester@app.com',
        'password': 'nicepassword'}
    transaction = {
        'value': 1200,
        'description': 'Regular Salary',
        'account_source': 1,
        'account_destination': 2}

    def create_test_user(self, _db, test_user=None):
        if test_user is None:
            test_user = self.test_user
        user = User(username=test_user['username'], email=test_user['email'])
        user.set_password(test_user['password'])
        _db.session.add(user)

    @pytest.fixture(scope='class')
    def user_with_default_accounts(self, app):
        """Helper function to create user and init default accounts."""
        with app.app_context():
            db.create_all()
            self.create_test_user(db)
            user = User.query.filter_by(username=self.test_user['username']).first()
            user.init_accounts()
            yield user
            db.drop_all()

    @pytest.fixture(scope='class')
    def app_db_with_test_user(self, app):
        with app.app_context():
            db.create_all()
            self.create_test_user(db)
            yield db
            db.session.rollback()

    def create_transaction(self, _db, transaction=None):
        if transaction is None:
            transaction = self.transaction
        _db.session.add(Transaction(**transaction))
