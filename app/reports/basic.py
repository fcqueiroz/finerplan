from datetime import date
from dateutil.relativedelta import relativedelta

from flask_login import current_user

from app.dates import special_dates as sdates
from app.models import Account


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

    # This only works when we deal with a leaf node.
    # It doesn't calculate balance of account's descendents
    _balance = equity_account.balance(end=period_end)
    return _balance


def income_and_expenses(account) -> float:
    """
    Evaluates total earnings/expenses in the current month.

    Parameters
    ----------
    account: str {'Earnings', 'Expenses'}
        Account name to perform the calculation
    """
    period_start = sdates.start_of_current_month()
    period_end = sdates.start_of_next_month()
    return _income_and_expenses(account, start=period_start, end=period_end)


def _income_and_expenses(account, **kwargs) -> float:
    """
    Evaluates total earnings/expenses in any time period.

    Parameters
    ----------
    account: str {'Earnings', 'Expenses'}
        Account name to perform the calculation
    """
    _account_name = account
    if _account_name in ('Earnings', 'Expenses'):
        user_id = current_user.id
        account = Account.query.filter_by(name=account, user_id=user_id).first()
    else:
        raise ValueError(f'Unknown account type "{account}"')

    # This only works when we deal with a leaf node. It
    # doesn't calculate balance of account's descendents.
    _result = account.balance(**kwargs)
    if _account_name == 'Earnings':
        # Because transactions only flow out of Earnings, we must
        # invert the signal to get a positive value.
        _result = - _result

    return _result


def month_savings() -> float:
    earnings = income_and_expenses(account='Earnings')
    expenses = income_and_expenses(account='Expenses')
    return earnings - expenses


def savings_rate(lenght=12) -> str:
    """
    Calculates savings rate over a period of time.

    Parameters
    ---------
    lenght: int
        Number of months in the past to include in the calculation.
    """
    period_start = sdates.start_of_current_month() - relativedelta(months=lenght)
    period_end = sdates.start_of_next_month()

    losses = _income_and_expenses(account='Expenses', start=period_start, end=period_end)
    profits = _income_and_expenses(account='Earnings', start=period_start, end=period_end)

    if profits == 0:
        return "No earnings during period."
    elif losses > profits:
        return "No savings in period. (expenses greater than earnings)"
    else:
        rate = 1 - losses / profits
        return '{0:.1f} %'.format(100 * rate)
