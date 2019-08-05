from datetime import datetime
import pytest

from finerplan.model import Transaction


@pytest.mark.usefixtures('test_transactions')
def test_transaction_balance_method_unbounded(test_accounts):
    """Tests generic method to calculate transactions's balance over a period of time."""
    account = test_accounts[2]

    assert Transaction.balance(account) == 1135


@pytest.mark.usefixtures('test_transactions')
def test_transaction_balance_method_bounded(test_accounts):
    """Tests generic method to calculate transactions's balance over a period of time."""
    account = test_accounts[2]

    dt = datetime(2019, 7, 15)

    assert Transaction.balance(account, end=dt) == 1185
    assert Transaction.balance(account, start=dt) == -50
    assert Transaction.balance(account, start=datetime(2019, 7, 3), end=dt) == -15
