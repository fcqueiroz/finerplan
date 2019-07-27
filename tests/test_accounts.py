from flask import url_for

from tests.test_auth import fill_login_form


def test_accounts_add(client, test_accounts):
    earnings = test_accounts[1]
    form = dict(name='Scholarship', parent_id=earnings.id)

    with client:
        client.post(url_for('simple_page.login'), data=fill_login_form(), follow_redirects=True)

        rv = client.post(url_for('simple_page.accounts'), data=form, follow_redirects=True)
        assert b'Earnings - Scholarship' in rv.data
