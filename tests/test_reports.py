from datetime import date
from unittest.mock import patch

import pytest

from app.reports import Report


@pytest.mark.usefixtures('test_transactions')
@patch('app.reports.basic.current_user')
def test_report_basic_balance(mock_user, test_user):
    mock_user.id = test_user.id
    period_end = date(2019, 7, 15)
    assert Report().basic.balance(period_end=period_end) == 1185


@pytest.mark.parametrize(
    ('account', 'result'),
    [('Earnings', 1200), ('Expenses', 65)])
@pytest.mark.usefixtures('test_transactions')
@patch('app.dates.special_dates.date')
@patch('app.reports.basic.current_user')
def test_report_basic_income_and_expenses(mock_user, mock_date, test_user, account, result):
    mock_user.id = test_user.id
    mock_date.today.return_value = date(2019, 7, 15)
    assert Report().basic.income_and_expenses(account=account) == result


@pytest.mark.usefixtures('test_transactions')
@patch('app.dates.special_dates.date')
@patch('app.reports.basic.current_user')
def test_report_basic_savings_rate(mock_user, mock_date, test_user):
    mock_user.id = test_user.id
    mock_date.today.return_value = date(2019, 8, 1)

    rate = 1135 / 1200
    assert Report().basic.savings_rate() == '{0:.1f} %'.format(100 * rate)

