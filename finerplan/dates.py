from datetime import date
from datetime import datetime
from datetime import timedelta

from .finerplan import app

__MODEL = '%Y-%m-%d'
TODAY = date.today()

def date_converter(_date):
    if type(_date)==str:
        _date = datetime.strptime(_date, __MODEL).date()
    elif type(_date)==date:
        _date = _date
    else:
        raise Exception('Wrong Date Type: {}'.format(type(_date)))
    return _date

def next_month(_date, start=False):
    """Returns the last day of the month for a given date
    by default. If start=True then returns the 1st day of
    the given date's next month.
    """
    _date = date_converter(_date)
    next_month = improved_delta(_date, months=1).replace(day=1)
    if start:
        return next_month
    else:
        return next_month - timedelta(days=1)

def cash(_date):
    """Returns the date when a certain expense will be
    paid (cash date) for a given date instance (usually
    accrual date) according to the app's date for
    closing the invoice.
    """
    _date = date_converter(_date)
    cash_date = _date.replace(day=app.config['CREDIT_PAYMENT'])
    if _date.day > app.config['CREDIT_CLOSING']:
        cash_date = improved_delta(cash_date, months=1)
    return cash_date

def improved_delta(_date, years=0, months=0, weeks=0, days=0):
    """Improves standard timedelta to add new deltas (years,
    months and weeks). This is better suited for dealing
    with bigger time periods.
    """
    _date = date_converter(_date)
    new_date = _date + timedelta(days=(weeks*7 + days))
    dMonth = new_date.month + months
    dYear = new_date.year + years
    while dMonth > 12:
        dMonth = dMonth - 12
        dYear = dYear + 1
    while dMonth < 1:
        dMonth = dMonth + 12
        dYear = dYear - 1
    return date(dYear, dMonth, new_date.day)

def credit_state():
    if ((TODAY.day > app.config['CREDIT_CLOSING'])
        and (TODAY.day <= app.config['CREDIT_PAYMENT'])):
        return True
    else:
        return False

SOCM = TODAY.replace(day=1)  # Start Of Current Month
EOM = next_month(TODAY)  # End Of [current] Month
SOM = next_month(TODAY, start=True)  # Start Of [next] Month
# Date of credit card's next payment
NEXT_PAY = TODAY.replace(day=app.config['CREDIT_PAYMENT'])
if TODAY.day > app.config['CREDIT_PAYMENT']:
    NEXT_PAY = improved_delta(NEXT_PAY, months=1)
