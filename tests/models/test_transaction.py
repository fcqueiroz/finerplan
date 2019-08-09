from dateutil.relativedelta import relativedelta

from datetime import datetime
import pytest

from finerplan.model import Transaction, Account

from data.tests.transactions import computer


@pytest.mark.usefixtures('test_transactions')
def test_transaction_balance_method_unbounded():
    """Tests generic method to calculate transactions's balance over a period of time."""
    account = Account.query.filter_by(name='Cash').one()

    assert Transaction.balance(account) == 1135


@pytest.mark.usefixtures('test_transactions')
def test_transaction_balance_method_bounded():
    """Tests generic method to calculate transactions's balance over a period of time."""
    account = Account.query.filter_by(name='Cash').one()

    dt = datetime(2019, 7, 15)

    assert Transaction.balance(account, end=dt) == 1185
    assert Transaction.balance(account, start=dt) == -50
    assert Transaction.balance(account, start=datetime(2019, 7, 3), end=dt) == -15


@pytest.mark.usefixtures('test_accounts')
def test_transaction_create():
    """
    Tests that method 'create' can handle the data from AddTransactionForm
    and create both Transaction and Installment instances.
    """
    source = Account.query.filter_by(name='Visa 3412').one()
    destination = Account.query.filter_by(name='Computer').one()
    transaction_data = computer()
    value = transaction_data.pop('value')
    installments = transaction_data.pop('installments')

    transaction = Transaction.create(
        value=value, installments=installments, source_id=source.id,
        destination_id=destination.id, **transaction_data)

    assert Transaction.query.count() == 1
    assert transaction.installments.count() == installments

    expected = [
        dict(cash_date=transaction.accrual_date + relativedelta(day=source.payment), value=900.03),
        dict(cash_date=transaction.accrual_date + relativedelta(months=1, day=source.payment), value=900.00),
        dict(cash_date=transaction.accrual_date + relativedelta(months=2, day=source.payment), value=900.00),
        dict(cash_date=transaction.accrual_date + relativedelta(months=3, day=source.payment), value=900.00)]

    result = source.list_installments(transaction=transaction, installments=4, value=value)

    assert result == expected
