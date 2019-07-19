# Standard Library

# 3rd Party Libraries
from flask_login import current_user
import pytest
# Local Imports
from app.models import User
from tests.conftest import RoutingMixin, UserMixin


class BasicAuth(UserMixin):

    def login(self, client, username=None, password=None, query_string=None):
        """Login helper function"""
        if username is None:
            username = self.test_user['username']
        if password is None:
            password = self.test_user['password']
        
        return client.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True, query_string=query_string)

    @staticmethod
    def logout(client):
        """Logout helper function"""
        return client.get('/logout', follow_redirects=True)
    
    def register(self, client, username=None, password=None, email=None):
        """Register new user helper function"""
        if username is None:
            username = self.test_user['username']
        if password is None:
            password = self.test_user['password']
        if email is None:
            email = self.test_user['email']
        
        return client.post('/register', data=dict(
            username=username,
            password=password,
            password2=password,
            email=email
        ), follow_redirects=True)


@pytest.mark.usefixtures('app_db_with_test_user')
class TestUserAuth(RoutingMixin, BasicAuth):

    def test_successful_login(self, client):
        with client:
            self.login(client)
            assert self.test_user['username'] in str(current_user)

    def test_successful_logout(self, client):
        with client:
            self.login(client)
            assert self.test_user['username'] in str(current_user)
            self.logout(client)
            assert self.test_user['username'] not in str(current_user)

    def test_wrong_username(self, client):
        rv = self.login(client, username=self.test_user['username'] + 'x')
        assert b'Invalid username' in rv.data

    def test_wrong_password(self, client):
        rv = self.login(client, password=self.test_user['password'] + 'x')
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
    def test_login_redirects_to_private_url(self, client, url):
        title = ('<title>' + url.replace('/', '').capitalize()).encode('ascii')
        with client:
            query_string = {'next':  url}
            response = self.login(client, query_string=query_string)
            assert title in response.data


class TestUserRegister(RoutingMixin, BasicAuth):
    def test_register_page_exists(self, client):
        url = '/register'
        response = client.get(url)
        self.check_200_status_code(response, url)
        self.check_content_type(response, url)

    def test_successful_register(self, client, app_db):
        """Tests that a user can register in app"""
        self.register(client)

        user = app_db.session.query(User).filter_by(username=self.test_user['username']).first()
        assert user is not None
