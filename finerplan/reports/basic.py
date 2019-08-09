from datetime import date
from dateutil.relativedelta import relativedelta

from flask_login import current_user
from sqlalchemy import or_

from finerplan.model import Account, Transaction, AccountingGroup

from config import report_names


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
        super().__init__(report=report, available_reports=report_names['Information'])

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
    def _transaction_balance(names, **kwargs) -> float:
        """
        Evaluates the balance (ie deposits minus withdraws) in any time period.

        Parameters
        ----------
        names: list-like
            Accounting types to select when performing the calculation
        """
        names_filter = [(group_name == Account.group) for group_name in names]
        accounts = Account.query.filter(or_(*names_filter), Account.user_id == current_user.id)

        # TODO Remove the loop and make this calculation inside database!
        _result = 0
        for account in accounts:
            _result += Transaction.balance(account, **kwargs)

        return _result

    def current_balance(self) -> None:
        """
        Evaluates equity balance at present date.
        """
        self._text = 'Your current balance is:'
        self._value = self._transaction_balance(names=['Asset', 'Cash', 'Bank'], end=date.today())

    def current_month_income(self) -> None:
        """
        Evaluates total income in the current month.
        """
        self._text = 'Current month income:'
        self._value = -self._transaction_balance(names=['Income'], start=self._month_start, end=self._month_end)

    def current_month_expenses(self) -> None:
        """
        Evaluates total expenses in the current month.
        """
        self._text = 'Current month expenses:'
        self._value = self._transaction_balance(names=['Expense'], start=self._month_start, end=self._month_end)

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

        return bold(_formatter)

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

        _expenses = self._transaction_balance(names=['Expense'], start=period_start, end=period_end)
        _income = -self._transaction_balance(names=['Income'], start=period_start, end=period_end)

        if _income == 0:
            msg = "No income during period."
        elif _expenses > _income:
            msg = "No savings in period. (expenses greater than income)"
        else:
            msg = None
            self._value = 1 - _expenses / _income

        setattr(self, '_formatter', self._percent_formatter(msg=msg))
