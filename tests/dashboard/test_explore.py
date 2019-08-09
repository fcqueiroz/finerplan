import json

from flask import url_for
import pytest

from finerplan.model import add_common_accounts

from tests.test_auth import fill_login_form


@pytest.mark.parametrize(
    ('transaction_kind', 'source_idx', 'destination_idx'),
    [('income', 1, 2), ('expenses', 2, 4)])
def test_get_lead_accounts_json(client, test_accounts, transaction_kind, source_idx, destination_idx):

    with client:
        client.post(url_for('auth.login'), data=fill_login_form(), follow_redirects=True)
        rv = client.get(url_for('dashboard.accounts_json', transaction_kind=transaction_kind))

        source = test_accounts[source_idx]
        destination = test_accounts[destination_idx]

        assert json.loads(rv.data)['sources'][0]['name'] == source.fullname
        assert json.loads(rv.data)['destinations'][0]['name'] == destination.fullname


def test_accounts_json_issue_1(client, test_user):

    with client:
        client.post(url_for('auth.login'), data=fill_login_form(), follow_redirects=True)
        add_common_accounts(test_user)
        assert test_user.accounts.count() > 0

        rv = client.get(url_for('dashboard.accounts_json', transaction_kind='expenses'))
        rv = json.loads(rv.data)

        assert len(rv['destinations']) == 29
        assert len(rv['sources']) == 1
