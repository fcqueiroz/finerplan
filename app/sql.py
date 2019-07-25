from datetime import datetime
from dateutil.relativedelta import relativedelta
import os

import sqlite3

from app.dates import special_dates as sdate

from config import basedir, date_model

# Temporarily connects only to the old database (until we can move all functions to new database)
database = os.path.join(basedir, 'old.db')
con = sqlite3.connect(database, check_same_thread=False)
cur = con.cursor()


def sum_query(query_str, query_values):
    cur.execute('SELECT sum(value) FROM ' + query_str, query_values)
    result = cur.fetchone()[0]
    if not isinstance(result, (int, float)):
        result = 0
    return result


def exponential_moving_average(alpha=0.15, beta=0.5, kind='simple'):
    """
    Calculates Exponential Moving Average for monthly expenses.
    The EMA can be simple or double.
    """

    # Include code to check if kind == simple/Double
    query = 'select accrual_date from expenses order by accrual_date;'
    cur.execute(query)
    try:
        oldest_date = cur.fetchone()[0]
    except TypeError:
        # The database is probably empty
        return 0

    month_start = datetime.strptime(oldest_date, date_model).date()
    month_ending = month_start + relativedelta(day=31)

    cur.execute('SELECT sum(value) FROM expenses '
                'WHERE accrual_date>=? AND accrual_date <=?;',
                (month_start, month_ending))
    mov_avg = cur.fetchone()[0]
    if not isinstance(mov_avg, (int, float)):
        return 0
    if kind == 'double':
        month_start = month_ending + relativedelta(days=1)
        if month_start == sdate.start_of_current_month():
            # Not enough data for making a double EMA
            return mov_avg
        month_ending = month_start + relativedelta(day=31)
        cur.execute('SELECT sum(value) FROM expenses '
                    'WHERE accrual_date>=? AND accrual_date <=?;',
                    (month_start, month_ending))
        result = cur.fetchone()[0]
        if not isinstance(result, (int, float)):
            # Not enough data for making a double EMA
            return mov_avg
        else:
            trend = result - mov_avg
            mov_avg = result

    while True:
        month_start = month_ending + relativedelta(days=1)
        month_ending = month_start + relativedelta(day=31)

        cur.execute('SELECT sum(value) FROM expenses '
                    'WHERE accrual_date>=? AND accrual_date <=?;',
                    (month_start, month_ending))
        result = cur.fetchone()[0]
        if (not isinstance(result, (int, float))) or (month_start == sdate.start_of_current_month()):
            if kind == 'simple':
                return mov_avg
            elif kind == 'double':
                return mov_avg + 1 * trend
        if kind == 'simple':
            mov_avg = alpha*result + (1-alpha)*mov_avg
        elif kind == 'double':
            tmp = mov_avg
            mov_avg = alpha * result + (1 - alpha) * (tmp + trend)
            trend = beta * (mov_avg - tmp) + (1 - beta) * trend


def generate_month_expenses_table_data(start_date, final_date):
    query = ("SELECT category,sum(value) "
             "FROM expenses "
             "WHERE accrual_date >= ? and accrual_date < ? "
             "GROUP BY category;")
    cur.execute(query, (start_date, final_date))
    return cur.fetchall()
