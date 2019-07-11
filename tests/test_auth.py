# Standard Library

# 3rd Party Libraries
import pytest
# Local Imports


class TestBasicAuth(object):
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

    def test_successful_login(self, app, client):
        """Test login using helper functions"""
        rv = self.login(client, app.config['USERNAME'], app.config['PASSWORD'])
        assert b'You were logged in' in rv.data

    @pytest.mark.skip()
    def test_successful_logout(self, app, client):
        _ = self.login(client, app.config['USERNAME'], app.config['PASSWORD'])
        rv = self.logout(client)
        assert b'You were logged out' in rv.data

    def test_wrong_username(self, app, client):
        rv = self.login(client, app.config['USERNAME'] + 'x', app.config['PASSWORD'])
        assert b'Invalid username' in rv.data

    def test_wrong_password(self, app, client):
        rv = self.login(client, app.config['USERNAME'], app.config['PASSWORD'] + 'x')
        assert b'Invalid password' in rv.data
