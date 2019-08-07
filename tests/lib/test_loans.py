from datetime import datetime

import pytest

from finerplan.lib.loans import monthly_invoice, instant_transfer


def test_instant_transfer():
    dt = datetime(2019, 7, 10)
    fake_transaction = dict(accrual_date=dt, value=341.09)
    expected = [dict(cash_date=dt, value=341.09)]

    assert expected == instant_transfer(**fake_transaction)


@pytest.mark.parametrize(
    ('accrual_date', 'installments', 'result'), [
        (datetime(2019, 7, 10), 1, [dict(cash_date=datetime(2019, 7, 28), value=341.09)]),
        (datetime(2019, 7, 10), 2, [
            dict(cash_date=datetime(2019, 7, 28), value=170.55),
            dict(cash_date=datetime(2019, 8, 28), value=170.54)]),
        (datetime(2019, 7, 20), 1, [dict(cash_date=datetime(2019, 8, 28), value=341.09)]),
        (datetime(2019, 7, 20), 3, [
            dict(cash_date=datetime(2019, 8, 28), value=113.71),
            dict(cash_date=datetime(2019, 9, 28), value=113.69),
            dict(cash_date=datetime(2019, 10, 28), value=113.69)])])
def test_monthly_invoice(accrual_date, installments, result):
    fake_transaction = dict(accrual_date=accrual_date, value=341.09, installments=installments)

    closing_day = 14
    payment_day = 28

    assert result == monthly_invoice(closing_day=closing_day, payment_day=payment_day, **fake_transaction)

