from datetime import date

from flask_login import current_user

from app.models import Account

from app.sql import sum_query, exponential_moving_average
from app.dates import special_dates as sdates
from .credit_card import total_invoice_debt


def balance(period_end=None) -> float:
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


# Not ready for using new database yet
def free_balance() -> float:
    return balance() - total_invoice_debt()


def income_and_expenses(account) -> float:
    """
    Evaluates total earnings/expenses in the current month.

    Parameters
    ----------
    account: str {'Earnings', 'Expenses'}
        Account name to perform the calculation
    """
    if account in ('Earnings', 'Expenses'):
        user_id = current_user.id
        earnings_account = Account.query.filter_by(name=account, user_id=user_id).first()
    else:
        raise ValueError(f'Unknown account type "{account}"')

    socm = sdates.start_of_current_month()
    som = sdates.start_of_next_month()
    _result = earnings_account.balance(start=socm, end=som)
    if account == 'Earnings':
        _result = - _result

    return _result


# Not ready for using new database yet
def double_ema():
    return exponential_moving_average(kind='double')


def month_savings() -> float:
    earnings = income_and_expenses(account='Earnings')
    expenses = income_and_expenses(account='Expenses')
    return earnings - expenses


# Not ready for using new database yet
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
