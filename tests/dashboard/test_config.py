from flask import url_for
import pytest

from finerplan.model import Card

from tests.test_auth import fill_login_form
from data.tests.accounts import visa
from data.tests.card_report import test_report, basic_report


@pytest.mark.usefixtures('test_user')
def test_accounts_add_credit_card(client):
    credit_card = visa()
    credit_card['group_id'] = credit_card['group'].id
    del credit_card['group']
    credit_card['parent_id'] = None

    with client:
        client.post(url_for('auth.login'), data=fill_login_form(), follow_redirects=True)
        rv = client.post(url_for('dashboard.accounts_create'), data=credit_card, follow_redirects=True)

        assert credit_card['name'].encode('utf-8') in rv.data


@pytest.mark.usefixtures('test_transactions')
def test_reports_list(client):
    """
    Tests that user can visit page to see all the already created reports.
    """
    with client:
        client.post(url_for('auth.login'), data=fill_login_form(), follow_redirects=True)
        rv = client.get(url_for('dashboard.reports_list'), follow_redirects=True)

        assert b'No reports cards created yet.' in rv.data


@pytest.mark.usefixtures('test_transactions')
def test_reports_add_card(client):
    """
    Tests that user can create a new report card.
    """
    new_report = test_report()
    with client:
        client.post(url_for('auth.login'), data=fill_login_form(), follow_redirects=True)
        rv = client.post(url_for('dashboard.reports_create'), data=new_report, follow_redirects=True)

    assert new_report['name'].encode('utf-8') in rv.data


@pytest.mark.usefixtures('test_transactions')
def test_report_card_add_multiple_reports(client):
    """
    Tests that user can create a new report card containing multiple reports.
    """
    new_report = basic_report()
    with client:
        client.post(url_for('auth.login'), data=fill_login_form(), follow_redirects=True)
        _ = client.post(url_for('dashboard.reports_create'), data=new_report, follow_redirects=True)

    card = Card.query.one()
    assert card.reports.count() == 4
    for i, report in enumerate(card.reports):
        assert report.name == new_report['information_names'][i]
