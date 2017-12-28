from .finerplan import app
from datetime import date
from datetime import datetime
from datetime import timedelta
model = '%Y-%m-%d'
tday = date.today()

def next_month(dtDateTime, start=False):
    """Returns the last day of the month for a given date by default
    If start=True then returns the 1st day of the given date's next month
    """
    next_month = months_delta(dtDateTime, 1)
    sonm = date(next_month.year, next_month.month, 1)
    if start:
        return sonm
    else:
        return sonm - timedelta(days=1)

def months_delta(original_date, months_delta):
    dYear = original_date.year
    dMonth = original_date.month + months_delta
    while dMonth > 12:
        dMonth = dMonth - 12
        dYear = dYear + 1
    while dMonth < 1:
        dMonth = dMonth + 12
        dYear = dYear - 1
    return date(dYear, dMonth, original_date.day)

# Date of next card payment
next_pay = date(tday.year, tday.month, app.config['CREDIT_PAYMENT'])
if tday.day > next_pay.day:
        next_pay = months_delta(next_pay, 1)

# Specific dates in string format
# socm: Start Of Current Month
# eom: End Of [current] Month
# som: Start Of [next] Month
s_socm = date(date.today().year,date.today().month,1).strftime(model)
s_eom = next_month(date.today()).strftime('%d/%b/%Y')
s_som = next_month(date.today(), start=True).strftime(model)

