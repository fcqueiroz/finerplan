from datetime import date
from unittest.mock import patch

import pytest

from finerplan.reports.basic import InformationReport


@pytest.mark.usefixtures('test_transactions')
@patch('finerplan.reports.basic.current_user')
@patch('finerplan.reports.basic.date')
def test_information_report_current_balance(mock_date, mock_user, test_user):
    """
    Tests the current balance information.
    """
    mock_user.id = test_user.id
    mock_date.today.return_value = date(2019, 7, 15)

    report = InformationReport(report='Current Balance')
    result = report.to_html()

    assert 'current balance' in result
    assert '1185' in result


@pytest.mark.usefixtures('test_transactions')
@patch('finerplan.reports.basic.current_user')
@patch('finerplan.reports.basic.date')
def test_information_report_income(mock_date, mock_user, test_user):
    """
    Tests the current month income information.
    """
    mock_user.id = test_user.id
    mock_date.today.return_value = date(2019, 7, 15)

    report = InformationReport(report='Current Month Income')
    result = report.to_html()

    assert 'current month income' in result
    assert '1200' in result


@pytest.mark.usefixtures('test_transactions')
@patch('finerplan.reports.basic.current_user')
@patch('finerplan.reports.basic.date')
def test_information_report_expenses(mock_date, mock_user, test_user):
    """
    Tests the current month expenses information.
    """
    mock_user.id = test_user.id
    mock_date.today.return_value = date(2019, 7, 15)

    report = InformationReport(report='Current Month Expenses')
    result = report.to_html()

    assert 'current month expenses' in result
    assert '65' in result


@pytest.mark.usefixtures('test_transactions')
@patch('finerplan.reports.basic.current_user')
@patch('finerplan.reports.basic.date')
def test_information_report_savings_rate(mock_date, mock_user, test_user):
    """
    Tests the current month expenses information.
    """
    mock_user.id = test_user.id
    mock_date.today.return_value = date(2019, 8, 1)

    report = InformationReport(report='Savings Rate')
    result = report.to_html()

    assert 'months savings rate' in result
    assert '{0:.1f} %'.format(100 * 1135 / 1200) in result
