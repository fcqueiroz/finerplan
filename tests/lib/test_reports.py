from datetime import date
from unittest.mock import patch

import pytest

from finerplan.lib.reports import Report


@pytest.mark.usefixtures('test_transactions')
@patch('finerplan.lib.reports.basic.current_user')
@patch('finerplan.lib.reports.basic.date')
def test_report_basic_balance(mock_date, mock_user, test_user):
    mock_user.id = test_user.id
    mock_date.today.return_value = date(2019, 7, 15)
    assert Report().basic.balance() == 1185


@pytest.mark.usefixtures('test_transactions')
@patch('finerplan.lib.reports.basic.current_user')
@patch('finerplan.lib.reports.basic.date')
def test_report_basic_earnings(mock_date, mock_user, test_user):
    mock_user.id = test_user.id
    mock_date.today.return_value = date(2019, 7, 15)
    assert Report().basic.income() == 1200


@pytest.mark.usefixtures('test_transactions')
@patch('finerplan.lib.reports.basic.current_user')
@patch('finerplan.lib.reports.basic.date')
def test_report_basic_expenses(mock_date, mock_user, test_user):
    mock_user.id = test_user.id
    mock_date.today.return_value = date(2019, 7, 15)
    assert Report().basic.expenses() == 65


@pytest.mark.usefixtures('test_transactions')
@patch('finerplan.lib.reports.basic.current_user')
@patch('finerplan.lib.reports.basic.date')
def test_report_basic_savings_rate(mock_date, mock_user, test_user):
    mock_user.id = test_user.id
    mock_date.today.return_value = date(2019, 8, 1)

    rate = 1135 / 1200
    assert Report().basic.savings_rate() == '{0:.1f} %'.format(100 * rate)

