from datetime import date

from app.sql import SqliteOps
from app.dates import special_dates as sdates
from .credit_card import total_invoice_debt

sql = SqliteOps()


def balance():
    today = date.today()
    
    values = (today,)
    query = 'expenses WHERE (cash_date <= ?);'
    t_gasto = sql.sum_query(query, values)
    query = 'earnings WHERE (cash_date <= ?);'
    t_renda = sql.sum_query(query, values)
    query = 'brokerage_transfers WHERE (cash_date <= ?) AND (origin = ?);'
    values = (today, 'Personal')
    t_brokerage_transfers = sql.sum_query(query, values)
    
    return t_renda - t_gasto - t_brokerage_transfers


def free_balance():
    return balance() - total_invoice_debt()


def earnings():
    socm = sdates.start_of_current_month()
    som = sdates.start_of_next_month()
    values = (socm, som)
    query = 'earnings WHERE ((? <= accrual_date) and (accrual_date < ?));'
    return sql.sum_query(query, values)


def expenses():
    socm = sdates.start_of_current_month()
    som = sdates.start_of_next_month()
    values = (socm, som)
    query = 'expenses WHERE ((? <= accrual_date) and (accrual_date < ?));'
    return sql.sum_query(query, values)


def double_ema():
    return sql.ema(kind='double')


def month_savings():
    return earnings() - expenses()


def savings_rate():
    socm = sdates.start_of_current_month()
    som = sdates.start_of_next_month()
    values = (som, '-12 month', socm)
    query = ('expenses WHERE ((SELECT date(?, ?) <= accrual_date) '
             'and (accrual_date < ?));')
    out_12m = sql.sum_query(query, values)
    query = ('earnings WHERE ((SELECT date(?, ?) <= accrual_date) '
             'and (accrual_date < ?));')
    in_12m = sql.sum_query(query, values)
    if in_12m == 0:
        _rate = "Not available"
    else:
        _rate = '{0:.2f} %'.format(100 * (1 - out_12m / in_12m))

    return _rate
