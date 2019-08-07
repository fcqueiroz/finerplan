from datetime import date
from unittest.mock import patch

from flask import url_for
import pytest

from tests.test_auth import fill_login_form


@pytest.mark.usefixtures('test_card')
@patch('finerplan.reports.basic.current_user')
@patch('finerplan.reports.basic.date')
def test_reports_add_custom_card(mock_date, mock_user, client, test_user):
    """
    Tests that user can add a report card to Overview page.
    The report contains the current balance information.
    """
    mock_user.id = test_user.id
    mock_date.today.return_value = date(2019, 7, 15)

    with client:
        client.post(url_for('auth.login'), data=fill_login_form(), follow_redirects=True)

        rv = client.get(url_for('dashboard.overview'))

    assert b'Test Report' in rv.data
    # print(rv.data.decode())
    assert b'Your current balance is:' in rv.data
    assert b'<b>1185.00</b>' in rv.data
