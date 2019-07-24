from app.dates import helpers, special_dates as sdates
from app.sql import SqliteOps

sql = SqliteOps()

# This variable holds the user preference for maximum expending in luxyry
luxury_budget = 320


def expenses():
    socm = sdates.start_of_current_month()
    som = sdates.start_of_next_month()

    values = (socm, som)
    query = """expenses WHERE ((? <= accrual_date)
                               and (accrual_date < ?)
                               and (category = 'Restaurantes'
                                    or category = 'Lazer'));"""
    return sql.sum_query(query, values)


def available():
    return luxury_budget - expenses()


def rate():
    m_progress = helpers.month_progress()
    lux_rate = expenses() / (luxury_budget * m_progress)
    return '{0:.2f} %'.format(100*lux_rate)
