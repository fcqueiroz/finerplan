from datetime import date
from dateutil.relativedelta import relativedelta

from flask_login import current_user
from sqlalchemy import or_

from finerplan.model import Account, Transaction
from .history import Expenses


def bold(func):
    def wrapper(*args, **kwargs):
        return " <b>" + func(*args, **kwargs) + "</b>"

    return wrapper


class BaseReport(object):
    _report = None
    _value = None
    _name_mapper = None

    def __init__(self, report):
        if report in self.available_reports():
            self._report = self._name_mapper[report]
        else:
            raise ValueError(f"{type(self).__name__} doesn't provide report '{report}'")

    def to_html(self):
        raise NotImplementedError

    @classmethod
    def available_reports(cls):
        """Returns a list of all the implemented reports in this class."""
        try:
            return cls._name_mapper.keys()
        except AttributeError:
            raise NotImplementedError


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


class InformationReport(BaseReport):
    _text = None
    _name_mapper = {
        'Current Balance': 'current_balance',
        'Current Month Income': 'current_month_income',
        'Current Month Expenses': 'current_month_expenses',
        'Current Month Savings': 'current_month_savings',
        'Savings Rate': 'savings_rate'}

    def __init__(self, report, description=None):
        """
        Produces basic information reports (Descriptive text + Scalar value)

        Parameters
        ----------
        report: str
            Name of the report to be generated.
        description:
            Descriptive text that will appear together with the calculated value.
        """
        super().__init__(report=report)
        if description is not None:
            self.description = description

    def to_html(self):
        getattr(self, self._report)()
        formatted_value = self._formatter()
        description = getattr(self, 'description', self._text)
        return description + formatted_value

    @bold
    def _formatter(self):
        return '{0:.2f}'.format(self._value)

    def current_balance(self) -> None:
        """
        Evaluates equity balance at present date.
        """
        self._text = 'Your current balance is:'
        self._value = _transaction_balance(names=['Asset', 'Cash', 'Bank'], end=date.today())

    def current_month_income(self) -> None:
        """
        Evaluates total income in the current month.
        """
        self._text = 'Current month income:'
        _today = date.today()
        self._value = -_transaction_balance(
            names=['Income'], start=_today + relativedelta(day=1), end=_today + relativedelta(day=31))

    def current_month_expenses(self) -> None:
        """
        Evaluates total expenses in the current month.
        """
        self._text = 'Current month expenses:'
        _today = date.today()
        self._value = _transaction_balance(
            names=['Expense'], start=_today + relativedelta(day=1), end=_today + relativedelta(day=31))

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

        period_end = date.today() + relativedelta(day=1)
        period_start = period_end - relativedelta(months=length)

        _expenses = _transaction_balance(names=['Expense'], start=period_start, end=period_end)
        _income = -_transaction_balance(names=['Income'], start=period_start, end=period_end)

        if _income == 0:
            msg = "No income during period."
        elif _expenses > _income:
            msg = "No savings in period. (expenses greater than income)"
        else:
            msg = None
            self._value = 1 - _expenses / _income

        setattr(self, '_formatter', self._percent_formatter(msg=msg))


class TableReport(BaseReport):
    _name_mapper = {
        # 'Recent Transactions': 'recent_transactions',
        'Last 12 Month Expenses': 'last_12_month_expenses'}

    def to_html(self):
        getattr(self, self._report)()

        html = '<div class="data-tables">'
        html += self._value.to_html(
            table_id='dataTable2', classes='text-center', index=False).replace('border="1" ', '')
        html += '</div>'
        return html

    def recent_transactions(self):
        raise NotImplementedError

    def last_12_month_expenses(self) -> None:
        creator = Expenses(index_name='Category', mean_name='Mean', weight_name="Acc W..", sum_name='Sum')
        self._value = creator.table()

