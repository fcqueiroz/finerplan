
from flask import url_for
from flask_login import current_user
import pytest

from finerplan.model import User

from data.tests import users


def fill_login_form(username=None, password=None):
    """Login helper function"""
    _user = users.alice()
    if username is None:
        username = _user['username']
    if password is None:
        password = _user['password']
    return dict(username=username, password=password)


def fill_register_form(username=None, password=None, email=None):
    """Register new user helper function"""
    _user = users.alice()
    if username is None:
        username = _user['username']
    if email is None:
        email = _user['email']
    if password is None:
        password = _user['username']
    return dict(username=username, email=email,
                password=password, password2=password)


def test_register_page_exists(client):
    url = url_for('auth.register')
    response = client.get(url)
    assert 200 == response.status_code, f"wrong status code for '{url}'"
    assert 'text/html' in response.content_type, f"wrong content type for '{url}'"


def test_login_page_exists(client):
    url = url_for('auth.login')
    response = client.get(url)
    assert 200 == response.status_code, f"wrong status code for '{url}'"
    assert 'text/html' in response.content_type, f"wrong content type for '{url}'"


def test_overview_is_inaccessible_before_login(client):
    expected_query_string = f"{url_for('auth.login')}?next={'%2Foverview'}"
    title = '<title>Expenses'.encode('utf-8')

    response = client.get(url_for('dashboard.overview'))
    assert expected_query_string in str(response.headers)
    assert response.status_code == 302
    assert title not in response.data


def test_expenses_is_inaccessible_before_login(client):
    expected_query_string = f"{url_for('auth.login')}?next={'%2Fexpenses'}"
    title = '<title>Expenses'.encode('utf-8')
    
    response = client.get(url_for('dashboard.expenses'))
    assert expected_query_string in str(response.headers)
    assert response.status_code == 302
    assert title not in response.data


@pytest.mark.usefixtures('test_accounts')
def test_login_redirects_to_overview_by_default(client):
    title = '<title>Overview - FinerPlan</title>'.encode('utf-8')
    response = client.post(url_for('auth.login'), data=fill_login_form(), follow_redirects=True)
    assert title in response.data


@pytest.mark.usefixtures('test_user')
def test_login_redirects_with_next(client):
    title = '<title>Expenses - FinerPlan</title>'.encode('utf-8')

    query_string = {'next':  'expenses'}
    response = client.post(url_for('auth.login'), data=fill_login_form(),
                           follow_redirects=True, query_string=query_string)
    assert title in response.data


def test_successful_register(client, db_session):
    """Tests that a user can register in app"""
    alice = users.alice()

    form = fill_register_form(**alice)
    client.post(url_for('auth.register'), data=form)

    user = db_session.query(User).filter_by(username=alice['username'], email=alice['email']).first()
    assert user is not None


@pytest.mark.usefixtures('test_accounts')
def test_successful_login_logout(client, test_user):
    form = fill_login_form()
    with client:
        client.post(url_for('auth.login'), data=form, follow_redirects=True)
        assert test_user.username in str(current_user)

        client.get(url_for('auth.logout'), follow_redirects=True)
        assert test_user.username not in str(current_user)


@pytest.mark.usefixtures('test_user')
def test_wrong_username(client):
    form = fill_login_form(username='other_name')
    rv = client.post(url_for('auth.login'), data=form)
    assert b'Invalid username' in rv.data


@pytest.mark.usefixtures('test_user')
def test_wrong_password(client):
    form = fill_login_form(password='other_pass')
    rv = client.post(url_for('auth.login'), data=form)
    assert b'Invalid password' in rv.data
