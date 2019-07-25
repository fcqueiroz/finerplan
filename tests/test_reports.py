from datetime import date
from unittest.mock import patch

import pytest

from app.reports import Report


@pytest.mark.usefixtures('test_transactions')
@patch('app.reports.basic.current_user')
def test_report(mock_user, test_user):
    mock_user.id = test_user.id
    period_end = date(2019, 7, 15)
    assert Report().basic.balance(period_end=period_end) == 1185
