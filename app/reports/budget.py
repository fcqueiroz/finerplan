from datetime import date
from dateutil.relativedelta import relativedelta

from app.sql import sum_query

# This variable holds the user preference for maximum expending in luxyry
luxury_budget = 320


# Not ready for using new database yet
def expenses():
    socm = date.today().replace(day=1)
    som = date.today() + relativedelta(months=1, day=1)

    values = (socm, som)
    query = """expenses WHERE ((? <= accrual_date)
                               and (accrual_date < ?)
                               and (category = 'Restaurantes'
                                    or category = 'Lazer'));"""
    return sum_query(query, values)


# Not ready for using new database yet
def available():
    return luxury_budget - expenses()


def _month_progress():
    today = date.today()
    end_of_current_month = today + relativedelta(day=31)
    return today.day / end_of_current_month.day


# Not ready for using new database yet
def rate():
    budget_rate = expenses() / (luxury_budget * _month_progress())
    return '{0:.2f} %'.format(100 * budget_rate)
