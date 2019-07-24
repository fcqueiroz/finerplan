from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import os

import pandas as pd
import sqlite3

from app.dates import special_dates as sdate

from config import basedir, date_model

# Temporarily connects only to the old database (until we can move all functions to new database)
database = os.path.join(basedir, 'old.db')
con = sqlite3.connect(database, check_same_thread=False)
cur = con.cursor()


class SqliteOps(object):
    @staticmethod
    def sum_query(query_str, query_values):
        cur.execute('SELECT sum(value) FROM ' + query_str, query_values)
        result = cur.fetchone()[0]
        if not isinstance(result, (int, float)):
            result = 0
        return result

    @staticmethod
    def ema(alpha=0.15, beta=0.5, kind='simple'):
        """Calculates Exponential Moving Average
        for monthly expenses. The EMA can be simple or double
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

    @staticmethod
    def expenses_table(months=13):
        df = pd.DataFrame(columns=['Category'])
        for num in range(months-1, -1, -1):
            start_date = date.today() + relativedelta(day=1, months=-num)
            final_date = start_date + relativedelta(months=1)
            query = ("SELECT category,sum(value) "
                     "FROM expenses "
                     "WHERE accrual_date >= ? and accrual_date < ? "
                     "GROUP BY category;")
            cur.execute(query, (start_date, final_date))
            result = cur.fetchall()
            label = start_date.strftime('%m/%y')
            tmp = pd.DataFrame(result, columns=['Category', label])
            df = pd.merge(df, tmp, how='outer',
                          left_on='Category', right_on='Category')

        cols = list(df.columns)
        cols.pop(cols.index('Category'))
        cols = ['Category'] + cols
        df = df[cols]
        df.fillna(value=0, inplace=True)
        df["Média"] = df.iloc[:, :-1].mean(axis=1)
        df["Média"] = df["Média"].apply(lambda x: round(x,2))
        df = df.sort_values(by="Média", ascending=False)

        df["Peso Ac."] = df["Média"].cumsum() / df["Média"].sum()
        df["Peso Ac."] = df["Peso Ac."].apply(lambda x: "{0:.1f} %".format(100*x))

        soma = df.sum()
        soma.name = 'Soma'
        soma['Category'] = soma.name
        soma[-1] = ""
        df = df.append(soma)

        return df.to_html(classes='expenses', index=False)
