from datetime import date

from flask_login import current_user

from app.models import Account

from app.sql import sum_query, exponential_moving_average
from app.dates import special_dates as sdates
from .credit_card import total_invoice_debt


def balance(period_end=None):
    """
    Evaluates equity balance (ie deposits minus withdraws) until a certain date.

    Parameters
    ----------
    period_end: datetime like object
        The balance will be evaluated on all transactions from the beginning of
        time until the 'period_end' date.
    """
    user_id = current_user.id
    equity_account = Account.query.filter_by(name='Equity', user_id=user_id).first()

    if period_end is None:
        period_end = date.today()

    _balance = equity_account.balance(end=period_end)
    return _balance


def free_balance():
    return balance() - total_invoice_debt()


def earnings():
    socm = sdates.start_of_current_month()
    som = sdates.start_of_next_month()
    values = (socm, som)
    query = 'earnings WHERE ((? <= accrual_date) and (accrual_date < ?));'
    return sum_query(query, values)


def expenses():
    socm = sdates.start_of_current_month()
    som = sdates.start_of_next_month()
    values = (socm, som)
    query = 'expenses WHERE ((? <= accrual_date) and (accrual_date < ?));'
    return sum_query(query, values)


def double_ema():
    return exponential_moving_average(kind='double')


def month_savings():
    return earnings() - expenses()


def savings_rate():
    socm = sdates.start_of_current_month()
    som = sdates.start_of_next_month()
    values = (som, '-12 month', socm)
    query = ('expenses WHERE ((SELECT date(?, ?) <= accrual_date) '
             'and (accrual_date < ?));')
    out_12m = sum_query(query, values)
    query = ('earnings WHERE ((SELECT date(?, ?) <= accrual_date) '
             'and (accrual_date < ?));')
    in_12m = sum_query(query, values)
    if in_12m == 0:
        _rate = "Not available"
    else:
        _rate = '{0:.2f} %'.format(100 * (1 - out_12m / in_12m))

    return _rate
