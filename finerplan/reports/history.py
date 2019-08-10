from datetime import date
from dateutil.relativedelta import relativedelta

import pandas as pd

from finerplan.sql import generate_month_expenses_table_data


class Expenses(object):
    def __init__(self, index_name='Category', mean_name='Média',
                 weight_name="Peso Ac.", sum_name='Soma'):
        self.index_name = index_name
        self.mean_name = mean_name
        self.weight_name = weight_name
        self.sum_name = sum_name

    @staticmethod
    def _generate_month_expenses_dataframe(num):
        start_date = date.today() + relativedelta(day=1, months=-num)
        final_date = start_date + relativedelta(months=1)

        table_data = generate_month_expenses_table_data(start_date, final_date)

        label = start_date.strftime('%m/%y')
        new_df = pd.DataFrame(table_data, columns=['index', label])
        new_df = new_df.set_index('index')

        return new_df

    def _generate_expenses_dataframe(self, months):
        dataframes = [self._generate_month_expenses_dataframe(num) for num in range(months-1, -1, -1)]
        df = pd.concat(dataframes, axis=1, sort=False)
        df.index.name = self.index_name
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

    def table(self, months=13):
        df = self._generate_expenses_dataframe(months)

        df = self._add_mean_column(df, new_col_name=self.mean_name)

        df = self._add_cumulative_weight_column(df, mean_col=self.mean_name, new_col_name=self.weight_name)

        return self._append_total_sum_row(df, index_name=self.index_name, sum_name=self.sum_name)
