from datetime import date
from dateutil.relativedelta import relativedelta

from app.sql import SqliteOps

from config import UserInfo

sql = SqliteOps()


def state():
    """Tells whether the credit card invoice is already closed or not."""
    if ((date.today().day > UserInfo.CREDIT_CLOSING)
            and (date.today().day < UserInfo.CREDIT_PAYMENT)):
        return "Closed"
    else:
        return "Open"


def future_payments(position=0):
    """Get date of the future credit card's payments.

    position: int=0
        Returns the N-th payment date in the future.
    """
    dt = date.today().replace(day=UserInfo.CREDIT_PAYMENT)
    if date.today().day >= UserInfo.CREDIT_PAYMENT:
        dt = dt + relativedelta(months=1)
    dt = dt + relativedelta(months=position)
    return dt


def invoice_value(position=0):
    """Get value of the N-th credit card's payments in the future.

    position: int=0
        Returns the N-th payment value in the future.
    """
    query = 'expenses WHERE pay_method="Crédito" and cash_date=?'
    values = (future_payments(position),)
    _value = sql.sum_query(query, values)
    return _value


def total_invoice_debt():
    values = (future_payments(),)
    query = 'expenses WHERE pay_method="Crédito" and cash_date>=?'
    _total_invoice_debt = sql.sum_query(query, values)
    return _total_invoice_debt
