from datetime import date
from dateutil import relativedelta

from .special_dates import end_of_current_month

from config import UserInfo


def credit_state():
    """Tells whether the credit card invoice is already closed or not."""
    if ((date.today().day > UserInfo.CREDIT_CLOSING)
            and (date.today().day < UserInfo.CREDIT_PAYMENT)):
        return True
    else:
        return False


def credit_card_future_payments(position=0):
    """Get date of the future credit card's payments.

    position: int=0
        Returns the N-th payment date in the future.
    """

    # Date of credit card's next payment
    dt = date.today().replace(day=UserInfo.CREDIT_PAYMENT)
    if date.today().day >= UserInfo.CREDIT_PAYMENT:
        dt = dt + relativedelta(months=1)
    dt = dt + relativedelta(months=position)
    return dt


def month_progress():
    return date.today().day / end_of_current_month().day


def cash_date(_date):
    """Returns the date when a certain expense will be
    paid (cash date) for a given date instance (usually
    accrual date) according to the app's date for
    closing the invoice.
    """

    _cash_date = _date.replace(day=UserInfo.CREDIT_PAYMENT)
    if _date.day > UserInfo.CREDIT_CLOSING:
        _cash_date = _cash_date + relativedelta(months=1)
    return _cash_date

