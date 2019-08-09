import json

from flask import url_for

from finerplan.model import add_common_accounts

from tests.test_auth import fill_login_form


def test_accounts_json_payload_get_income(client, test_user):
    transaction_kind = 'income'
    with client:
        client.post(url_for('auth.login'), data=fill_login_form(), follow_redirects=True)
        add_common_accounts(test_user)
        assert test_user.accounts.count() > 0

        rv = client.get(url_for('dashboard.accounts_json', transaction_kind=transaction_kind))
        payload = json.loads(rv.data)['sources']

        assert len(payload) == 5
        for key in ('id', 'name', 'type'):
            assert payload[0][key]


def test_accounts_json_get_expenses(client, test_user):
    transaction_kind = 'expenses'
    with client:
        client.post(url_for('auth.login'), data=fill_login_form(), follow_redirects=True)
        add_common_accounts(test_user)
        assert test_user.accounts.count() > 0

        rv = client.get(url_for('dashboard.accounts_json', transaction_kind=transaction_kind))
        rv = json.loads(rv.data)

        assert len(rv['destinations']) == 29
        assert len(rv['sources']) == 1
