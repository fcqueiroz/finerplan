from datetime import date
from dateutil.relativedelta import relativedelta

from .special_dates import end_of_current_month

from config import UserInfo


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

