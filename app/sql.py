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
    def _generate_month_expenses_table_data(start_date, final_date):
        query = ("SELECT category,sum(value) "
                 "FROM expenses "
                 "WHERE accrual_date >= ? and accrual_date < ? "
                 "GROUP BY category;")
        cur.execute(query, (start_date, final_date))
        return cur.fetchall()

    def _generate_month_expenses_dataframe(self, num):
        start_date = date.today() + relativedelta(day=1, months=-num)
        final_date = start_date + relativedelta(months=1)

        table_data = self._generate_month_expenses_table_data(start_date, final_date)

        label = start_date.strftime('%m/%y')
        new_df = pd.DataFrame(table_data, columns=['Category', label])
        new_df = new_df.set_index('Category')

        return new_df

    def _generate_expenses_dataframe(self, months, index_name):
        dataframes = [self._generate_month_expenses_dataframe(num) for num in range(months-1, -1, -1)]
        df = pd.concat(dataframes, axis=1, sort=False)
        df.index.name = index_name
        df = df.reset_index()
        return df.fillna(value=0)

    @staticmethod
    def _add_mean_column(_df, new_col_name):
        _df[new_col_name] = _df.iloc[:, :-1].mean(axis=1).apply(lambda x: round(x, 2))
        return _df

    @staticmethod
    def _add_cumulative_weight_column(_df, mean_col, new_col_name):
        _df = _df.sort_values(by=mean_col, ascending=False)
        _df[new_col_name] = _df[mean_col].cumsum() / _df[mean_col].sum()
        _df[new_col_name] = _df[new_col_name].apply(lambda x: "{0:.1f} %".format(100 * x))
        return _df

    @staticmethod
    def _append_total_sum_row(_df, index_name, sum_name):
        soma = _df.sum()
        soma.name = sum_name
        soma[index_name] = soma.name
        soma[-1] = ""
        return _df.append(soma)

    def expenses_table(self, months=13):
        """This method is being created as an updated version of
        'expenses_table'. The old method is being used to generate
        the correct value so this method can be tested."""

        index_name = 'Category'
        df = self._generate_expenses_dataframe(months, index_name=index_name)

        mean_name = 'Média'
        df = self._add_mean_column(df, new_col_name=mean_name)

        weight_name = "Peso Ac."
        df = self._add_cumulative_weight_column(df, mean_col=mean_name, new_col_name=weight_name)

        sum_name = 'Soma'
        df = self._append_total_sum_row(df, index_name=index_name, sum_name=sum_name)

        return df.to_html(classes='expenses', index=False)
