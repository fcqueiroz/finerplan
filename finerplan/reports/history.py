from datetime import date
from dateutil.relativedelta import relativedelta

import pandas as pd
from sqlalchemy import func

from finerplan import db
from finerplan.model import Account, Transaction, AccountingGroup
from finerplan.model.transaction import Installment


class Expenses(object):
    def __init__(self, index_name='Category', mean_name='Média',
                 weight_name="Peso Ac.", sum_name='Soma'):
        self.index_name = index_name
        self.mean_name = mean_name
        self.weight_name = weight_name
        self.sum_name = sum_name

    def _generate_expenses_dataframe(self, months):
        # Extract from database as a pandas.DataFrame
        table_data = (
            db.session.query(Account, Transaction, Installment)
              .with_entities(
                Account.name,
                Transaction.accrual_date,
                func.sum(Installment.value))
              .join(Transaction, Transaction.destination_id == Account.id)
              .join(Installment)
              .join(AccountingGroup)
              .filter(AccountingGroup.group == 'Expense')
              .group_by(Account.name, Transaction.accrual_date)
        ).all()
        new_df = pd.DataFrame(table_data, columns=[self.index_name, 'Accrual', 'Value'])

        # Filter period to analyze
        start_date = date.today() + relativedelta(day=1, months=(1-months))
        final_date = date.today() + relativedelta(days=31)
        new_df = new_df.loc[(new_df['Accrual'] >= start_date) & (new_df['Accrual'] <= final_date)]

        # Transform dataframe to desired shape
        new_df['Value'] = new_df['Value'].apply(float)
        new_df['Accrual'] = pd.to_datetime(new_df['Accrual']).apply(lambda dt: dt.replace(day=1).strftime('%m/%y'))
        new_df = new_df.groupby([self.index_name, 'Accrual']).sum().iloc[:, 0].unstack('Accrual').fillna(0)

        return new_df

    def table(self, months=13):
        df = self._generate_expenses_dataframe(months)

        # Add mean column
        df[self.mean_name] = df.iloc[:, :-1].mean(axis=1).apply(lambda x: round(x, 2))

        # Add cumulative weight column
        df = df.sort_values(by=self.mean_name, ascending=False)
        df[self.weight_name] = df[self.mean_name].cumsum() / df[self.mean_name].sum()
        df[self.weight_name] = df[self.weight_name].apply(lambda x: "{0:.1f} %".format(100 * x))

        # Append total sum row
        soma = df.sum()
        soma.name = self.sum_name
        soma[self.weight_name] = ""
        df = df.append(soma)

        return df
