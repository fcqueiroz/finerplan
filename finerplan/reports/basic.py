from datetime import date
from dateutil.relativedelta import relativedelta

from flask_login import current_user

from finerplan.model import Account, Transaction

from config import information_report_kinds


def bold(func):
    def wrapper(*args, **kwargs):
        return " <b>" + func(*args, **kwargs) + "</b>"

    return wrapper


class BaseReport(object):
    _report = None
    _value = None
    _text = None

    def __init__(self, report, available_reports):
        self._find_report_method(report, available_reports)

    def to_html(self):
        getattr(self, self._report)()

        formatted_value = self._formatter()

        return self._text + formatted_value

    @bold
    def _formatter(self):
        return '{0:.2f}'.format(self._value)

    def _find_report_method(self, report, available_reports):
        if report in available_reports:
            report = self._kind_mapper(report)
            self._report = report
        else:
            raise ValueError(f"{type(self).__name__} doesn't provide report '{report}'")

    @staticmethod
    def _kind_mapper(kind):
        raise NotImplementedError


class InformationReport(BaseReport):

    def __init__(self, report):
        """
        Produces basic information reports (Descriptive text + Scalar value)

        Parameters
        ----------
        report: str
            Name of the report to be generated.
        """
        super().__init__(report=report, available_reports=information_report_kinds)

    @staticmethod
    def _kind_mapper(kind):
        return kind.lower().replace(' ', '_')

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

    def current_balance(self) -> None:
        """
        Evaluates equity balance at present date.
        """
        self._text = 'Your current balance is:'
        self._value = self._account_balance(account='Equity', end=date.today())

    def current_month_income(self) -> None:
        """
        Evaluates total income in the current month.
        """
        self._text = 'Current month income:'
        self._value = self._account_balance("Income", start=self._month_start, end=self._month_end)

    def current_month_expenses(self) -> None:
        """
        Evaluates total expenses in the current month.
        """
        self._text = 'Current month expenses:'
        self._value = self._account_balance("Expenses", start=self._month_start, end=self._month_end)

    def current_month_savings(self) -> None:
        """
        Evaluates total savings in the current month.
        """
        self._text = 'This month savings:'

        self.current_month_income()
        income = self._value

        self.current_month_expenses()
        expenses = self._value

        self._value = income - expenses

    def _percent_formatter(self, msg=None):

        def _formatter():
            if msg:
                return msg
            else:
                return '{0:.1f} %'.format(100 * self._value)

        return _formatter

    def savings_rate(self, length=12) -> None:
        """
        Calculates savings rate over a period of time.

        Parameters
        ---------
        length: int
            Number of months in the past to include in the calculation.
        """
        self._text = 'Last 12 months savings rate:'

        period_end = self._month_start
        period_start = period_end - relativedelta(months=length)

        _expenses = self._account_balance(account='Expenses', start=period_start, end=period_end)
        _income = self._account_balance(account='Income', start=period_start, end=period_end)

        if _income == 0:
            msg = "No income during period."
        elif _expenses > _income:
            msg = "No savings in period. (expenses greater than income)"
        else:
            msg = None
            self._value = 1 - _expenses / _income

        setattr(self, '_formatter', self._percent_formatter(msg=msg))
