# Standard Library

# 3rd Party Libraries
from flask_login import current_user
import pytest
# Local Imports
from app import db
from app.models import User
from tests.conftest import RoutingMixin


class BasicAuth(object):
    user = 'tester'
    email = user + '@app.com'
    password = 'nicepassword'

    @staticmethod
    def login(client, username, password):
        """Login helper function"""
        return client.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    @staticmethod
    def logout(client):
        """Logout helper function"""
        return client.get('/logout', follow_redirects=True)
    
    @staticmethod
    def register(client, username, password, email):
        """Register new user helper function"""
        return client.post('/register', data=dict(
            username=username,
            password=password,
            password2=password,
            email=email
        ), follow_redirects=True)


class TestUserAuth(BasicAuth):

    @pytest.fixture(scope='class')
    def db_with_created_user(self, app):
        user = User(username=self.user, email=self.email)
        user.set_password(self.password)

        with app.app_context():
            db.create_all()
            db.session.add(user)
            yield db
            db.session.rollback()
    
    def test_successful_login(self, client, db_with_created_user):
        with client:
            self.login(client, self.user, self.password)
            assert self.user in str(current_user)

    @pytest.mark.skip()
    def test_successful_logout(self, client, db_with_created_user):
        with client:
            self.login(client, self.user, self.password)
            assert self.user in str(current_user)
            self.logout(client)
            assert self.user not in str(current_user)

    def test_wrong_username(self, client, db_with_created_user):
        rv = self.login(client, self.user + 'x', self.password)
        assert b'Invalid username' in rv.data

    def test_wrong_password(self, client, db_with_created_user):
        rv = self.login(client, self.user, self.password + 'x')
        assert b'Invalid password' in rv.data


class TestUserRegister(RoutingMixin, BasicAuth):
    def test_register_page_exists(self, client):
        url = '/register'
        response = client.get(url)
        self.check_200_status_code(response, url)
        self.check_content_type(response, url)

    def test_successful_register(self, client, app_db):
        """Tests that a user can register in app"""
        self.register(client, username=self.user, password=self.password, email=self.email)

        user = app_db.session.query(User).filter_by(username=self.user).first()
        assert user is not None
