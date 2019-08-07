from finerplan.sql import exponential_moving_average

from .basic import BasicReport
from .credit_card import total_invoice_debt


# Not ready for using new database yet
def free_balance() -> float:
    return BasicReport().balance() - total_invoice_debt()


# Not ready for using new database yet
def double_ema():
    return exponential_moving_average(kind='double')
