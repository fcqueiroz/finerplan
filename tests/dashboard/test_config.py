from flask import url_for
import pytest

from tests.test_auth import fill_login_form
from tests.data.accounts import card_3412, turn_group_into_id


def test_accounts_add_income(client, test_accounts):
    income = test_accounts[1]
    form = dict(name='Scholarship', parent_id=income.id, group_id=income.group_id)

    with client:
        client.post(url_for('auth.login'), data=fill_login_form(), follow_redirects=True)

        rv = client.post(url_for('dashboard.config_accounts_create'), data=form, follow_redirects=True)
        assert b'Income - Scholarship' in rv.data


@pytest.mark.usefixtures('test_user')
def test_accounts_add_credit_card(client):
    credit_card = turn_group_into_id(card_3412())
    credit_card['parent_id'] = None

    with client:
        client.post(url_for('auth.login'), data=fill_login_form(), follow_redirects=True)
        rv = client.post(url_for('dashboard.config_accounts_create'), data=credit_card, follow_redirects=True)

        assert b'Credit Card 3412' in rv.data


@pytest.mark.usefixtures('test_transactions')
def test_report_list(client):
    """
    Tests that user can visit page to see all the already created reports.
    """
    with client:
        client.post(url_for('auth.login'), data=fill_login_form(), follow_redirects=True)
        rv = client.get(url_for('dashboard.config_report_list'), follow_redirects=True)

        assert b'No reports created yet' in rv.data
