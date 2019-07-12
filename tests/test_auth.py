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
    def login(client, username, password, query_string=None):
        """Login helper function"""
        return client.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True, query_string=query_string)

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


class TestUserAuth(RoutingMixin, BasicAuth):
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

    def test_login_page_exists(self, client):
        url = '/login'
        response = client.get(url)
        self.check_200_status_code(response, url)
        self.check_content_type(response, url)

    @pytest.mark.parametrize("url", ['/overview', '/expenses', '/assets'])
    def test_url_is_inaccessible_before_login(self, client, url):
        title = ('<title>' + url.replace('/', '').capitalize()).encode('ascii')
        with client:
            response = client.get(url)
            assert title not in response.data

    @pytest.mark.parametrize("url", ['/overview', '/expenses', '/assets'])
    def test_login_redirects_to_private_url(self, client, url, db_with_created_user):
        title = ('<title>' + url.replace('/', '').capitalize()).encode('ascii')
        with client:
            query_string = {'next':  url}
            response = self.login(client, self.user, self.password, query_string=query_string)
            assert title in response.data


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
