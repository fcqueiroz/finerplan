from datetime import date
from dateutil.relativedelta import relativedelta

from flask_login import current_user

from finerplan.model import Account, Transaction


class BasicReport(object):

    def __init__(self, kind=None):
        """
        kind: str
            Name of the method to use when this instance is called
        """
        self._kind = kind

    def __call__(self, **kwargs):
        if self._kind is not None and hasattr(self, self._kind):
            self._kind(**kwargs)

    @property
    def _month_start(self):
        return date.today() + relativedelta(day=1)

    @property
    def _month_end(self):
        return date.today() + relativedelta(day=31)

    @staticmethod
    def _account_balance(account, **kwargs) -> float:
        """
        Evaluates account balance (ie deposits minus withdraws) in any time period.

        Parameters
        ----------
        account: str {'Income', 'Expenses', 'Equity'}
            Account name to perform the calculation
        """
        _account_name = account
        if _account_name in ('Income', 'Expenses', 'Equity'):
            user_id = current_user.id
            account = Account.query.filter_by(name=account, user_id=user_id).first()
        else:
            raise ValueError(f'Unknown account type "{account}"')

        # This only works when we deal with a leaf node. It
        # doesn't calculate balance of account's descendents.
        _result = Transaction.balance(account, **kwargs)
        if _account_name == 'Income':
            # Because transactions only flow out of Income, we must
            # invert the signal to get a positive value.
            _result = - _result

        return _result

    def balance(self) -> float:
        """
        Evaluates equity balance at present date.
        """
        return self._account_balance(account='Equity', end=date.today())

    def income(self) -> float:
        """
        Evaluates total income in the current month.
        """
        return self._account_balance("Income", start=self._month_start, end=self._month_end)

    def expenses(self) -> float:
        """
        Evaluates total expenses in the current month.
        """
        return self._account_balance("Expenses", start=self._month_start, end=self._month_end)

    def savings(self) -> float:
        """
        Evaluates total savings in the current month.
        """
        return self.income() - self.expenses()

    def savings_rate(self, length=12) -> str:
        """
        Calculates savings rate over a period of time.

        Parameters
        ---------
        length: int
            Number of months in the past to include in the calculation.
        """
        period_end = self._month_start
        period_start = period_end - relativedelta(months=length)

        _expenses = self._account_balance(account='Expenses', start=period_start, end=period_end)
        _income = self._account_balance(account='Income', start=period_start, end=period_end)

        if _income == 0:
            return "No income during period."
        elif _expenses > _income:
            return "No savings in period. (expenses greater than income)"
        else:
            rate = 1 - _expenses / _income
            return '{0:.1f} %'.format(100 * rate)
