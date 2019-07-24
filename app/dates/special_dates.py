"""Creates a dictionary of special dates for easy access."""

from datetime import date
from dateutil.relativedelta import relativedelta


def start_of_current_month():
    return date.today().replace(day=1)


def end_of_current_month():
    return date.today() + relativedelta(day=31)


def start_of_next_month():
    return date.today() + relativedelta(months=1, day=1)
