"""Methods for calculating installments' information."""
from datetime import datetime
from dateutil.relativedelta import relativedelta


def instant_transfer(accrual_date, value):
    """
    Creates a single installment which  has the
    same date and value as the original transaction.

    Parameters
    ----------
    accrual_date: datetime
        When the transaction happened
    value: float
        Total transaction's value

    Returns
    -------
    list containing a single value
    """

    return [dict(cash_date=accrual_date, value=value)]


def monthly_invoice(
        accrual_date: datetime, value: float, installments: int,
        closing_day: int, payment_day: int) -> list:
    """
    Implements the Credit Card's default way for calculating installments.

    Parameters
    ----------
    accrual_date: datetime
        When the transaction happened
    value: float
        Total transaction's value
    installments: int
        Number of installments
    closing_day: int
        Closing Day of Credit Card Invoice
    payment_day: int
        Payment Day of Credit Card Invoice
    """
    decimal_places = 2

    # Calculate dates
    if accrual_date.day > closing_day:
        first_payment_date = accrual_date + relativedelta(months=1, day=payment_day)
    else:
        first_payment_date = accrual_date + relativedelta(day=payment_day)

    installment_dates = [first_payment_date + relativedelta(months=i) for i in range(0, installments)]

    # Calculate values
    def payment_value():
        _installments = installments
        total_monetary_units = value * pow(10, decimal_places)
        first_payment = total_monetary_units // _installments + total_monetary_units % _installments
        _installments -= 1
        yield first_payment / pow(10, decimal_places)

        other_payments = (total_monetary_units - first_payment) / _installments / pow(10, decimal_places)
        while _installments:
            _installments -= 1
            yield other_payments

    result = [dict(cash_date=dt, value=val) for dt, val in zip(installment_dates, payment_value())]

    return result
