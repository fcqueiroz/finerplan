import json

from flask import url_for
import pytest

from tests.test_auth import fill_login_form


def test_accounts_add(client, test_accounts):
    income = test_accounts[1]
    form = dict(name='Scholarship', parent_id=income.id, group_id=income.group_id)

    with client:
        client.post(url_for('auth.login'), data=fill_login_form(), follow_redirects=True)

        rv = client.post(url_for('dashboard.config_accounts'), data=form, follow_redirects=True)
        assert b'Income - Scholarship' in rv.data


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
