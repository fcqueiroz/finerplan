from app.dates import helpers, special_dates as sdates
from app.sql import sum_query

# This variable holds the user preference for maximum expending in luxyry
luxury_budget = 320


# Not ready for using new database yet
def expenses():
    socm = sdates.start_of_current_month()
    som = sdates.start_of_next_month()

    values = (socm, som)
    query = """expenses WHERE ((? <= accrual_date)
                               and (accrual_date < ?)
                               and (category = 'Restaurantes'
                                    or category = 'Lazer'));"""
    return sum_query(query, values)


# Not ready for using new database yet
def available():
    return luxury_budget - expenses()


# Not ready for using new database yet
def rate():
    m_progress = helpers.month_progress()
    lux_rate = expenses() / (luxury_budget * m_progress)
    return '{0:.2f} %'.format(100*lux_rate)
