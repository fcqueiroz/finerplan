import math
import sqlite3
from sqlite3 import OperationalError
import pandas as pd
from dateutil.relativedelta import *

from config import date_model, form_words
from finerplan import app, dates

con = sqlite3.connect(app.config['DATABASE'],  check_same_thread=False)
cur = con.cursor()


def sum_query(query_str, query_values):
    cur.execute('SELECT sum(value) FROM ' + query_str, query_values)
    result = cur.fetchone()[0]
    if not isinstance(result, (int, float)):
        result = 0
    return result


def ema(alpha=0.15, beta=0.5, kind='simple'):
    """Calculates Exponential Moving Average
    for monthly expenses. The EMA can be simple or double
    """

    # Include code to check if kind == simple/Double
    sdate = dates.sdate()
    SOCM = sdate['SOCM']
    query = 'select accrual_date from expenses order by accrual_date;'
    cur.execute(query)
    try:
        oldest_date = cur.fetchone()[0]
    except TypeError:
        # The database is probably empty
        return 0
    month_start = dates.date_converter(oldest_date)
    month_ending = month_start + relativedelta(day=31)

    cur.execute('SELECT sum(value) FROM expenses '
                'WHERE accrual_date>=? AND accrual_date <=?;',
                (month_start, month_ending))
    mov_avg = cur.fetchone()[0]
    if not isinstance(mov_avg, (int, float)):
        return 0
    if kind == 'double':
        month_start = month_ending + relativedelta(days=1)
        if month_start == SOCM:
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
        if (not isinstance(result, (int, float))) or (month_start == SOCM):
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


def transactions_table(kind=None, monthly=True, num=50):
    """Get last transaction entries in any database.

    Parameters
    ----------
    kind : str
        Name of the table in the database
    monthly : bool, default True
        Limits the table to the current month transactions
    num : int, default 50
        Maximum number of transactions to show
    """

    if monthly:
        sdate = dates.sdate()
        SOCM = sdate['SOCM'].strftime(date_model)
        SOM = sdate['SOM'].strftime(date_model)
        data_range = ('WHERE accrual_date >= "' + SOCM +
                      '" and accrual_date < "' + SOM + '" ')
    else:
        data_range = ''

    if kind == 'expenses':
        query = ('SELECT pay_method,accrual_date,description,category,sum(value) '
                 'FROM expenses '
                 + data_range +
                 'GROUP BY accrual_date, description '
                 'ORDER BY accrual_date DESC, id DESC '
                 'LIMIT ?;')
    elif kind == 'earnings':
        query = ('SELECT accrual_date,cash_date,description,category,value '
                 'FROM earnings '
                 + data_range +
                 'ORDER BY accrual_date DESC, id DESC '
                 'LIMIT ?;')
    elif kind == 'brokerage_transfers':
        query = ('SELECT accrual_date,cash_date,description,value '
                 'FROM brokerage_transfers '
                 + data_range +
                 'ORDER BY accrual_date DESC, id DESC '
                 'LIMIT ?;')

    cur.execute(query, (num,))
    return cur.fetchall()


def last_expenses(num=10):
    """Get last (default=10) entries in expenses database"""
    cur.execute(
        ('SELECT pay_method,accrual_date,'
            'description,category,sum(value) '
         'FROM expenses '
         'GROUP BY accrual_date, description '
         'ORDER BY accrual_date DESC, id DESC LIMIT ?;'),
        (num,))
    return cur.fetchall()


def last_earnings():
    """Get all the current month earnings"""
    sdate = dates.sdate()
    SOCM, SOM = sdate['SOCM'], sdate['SOM']
    cur.execute(
        ('SELECT accrual_date,cash_date,description,category,value '
         'FROM earnings '
         'WHERE accrual_date >= ? and accrual_date < ? '
         'ORDER BY accrual_date DESC, id DESC;'),
        (SOCM, SOM))
    return cur.fetchall()


def last_investments():
    """Get all the current month investments"""
    sdate = dates.sdate()
    SOCM, SOM = sdate['SOCM'], sdate['SOM']
    cur.execute(
        ('SELECT accrual_date,cash_date,description,value '
         'FROM brokerage_transfers '
         'WHERE accrual_date >= ? and accrual_date < ? '
         'ORDER BY accrual_date DESC, id DESC;'),
        (SOCM, SOM))
    return cur.fetchall()


def insert_entry(form):
    """This function takes the information provided
    by the AddTransactionForm and inserts new:
    (1) expenses
    (2) earnings
    (3) investments
    """
    accrual = form.date.data
    cash = accrual
    descr = form.description.data
    t_val = float(form.value.data.replace(',','.'))
    table = form.transaction.data
    if table == 'expenses':
        query_str = (table+' ( pay_method, accrual_date, cash_date, '
                     'description, category, value) Values(?, ?, ?, ?, ?, ?)')
        method = form.pay_method.data
        cat_0 = form.new_cat.data
        if cat_0 == "":
            cat_0 = form.cat_expense.data
        cat_1 = "Outras Despesas"
        cat_2 = "Outras Despesas"
        if method == form_words['credit']:
            cash = dates.cash(accrual)
            installments = form.installments.data
            installment_quotient = round(((100*t_val) // installments) / 100,2)
            installment_remainder = round(((100*t_val) % installments) / 100,2)
            t_val = round(( 100*(installment_quotient+installment_remainder) )
                            / 100,2)
        query_values = (method, accrual, cash, descr, cat_0, t_val)
        cur.execute(('INSERT INTO '+ query_str), query_values)
        if method == form_words['credit'] and installments > 1:
            t_val = installment_quotient
            for i in range(1, installments):
                cash = cash + relativedelta(months=1)
                query_values = (method, accrual, cash, descr, cat_0, t_val)
                cur.execute(('INSERT INTO '+ query_str), query_values)
        elif method == form_words['outsourced']:
            cur.execute(
                ('INSERT INTO earnings ('
                    'accrual_date, cash_date, description, category, value) '
                 'Values(?, ?, ?, ?, ?)'),
                (accrual, accrual, descr, "Subsídio", t_val))
    elif table == 'earnings':
        cat = form.new_cat.data
        if cat == "":
            cat = form.cat_earning.data
        query_str = (table+' (accrual_date, cash_date, description, '
                     'category, value) Values(?, ?, ?, ?, ?)')
        query_values = (accrual, cash, descr, cat, t_val)
        cur.execute(('INSERT INTO '+ query_str), query_values)
    elif table == 'brokerage_transfers':
        query_str = (table+' (accrual_date, cash_date, description, '
                     'value) Values(?, ?, ?, ?)')
        query_values = (accrual, cash, descr, t_val)
        cur.execute(('INSERT INTO '+ query_str), query_values)
    else:
        return 2  # Unknown table
    try:
        con.commit()
    except:
        return 1  # Failed to commit changes to database


def generate_categories(table='expenses'):
    """Generate a tuple containing all the unique categories."""

    if table in ['expenses', 'earnings']:
        query = f'SELECT category,count(category) AS cont FROM {table} GROUP BY category ORDER BY cont DESC;'

        try:
            cur.execute(query)
            super_cat = [(row[0], row[0]) for row in cur.fetchall()]
        except OperationalError:
            super_cat = [(el, el) for el in ['Category 1', 'Category 2', 'Category 3']]
        return super_cat


def expenses_table(months=13):
    df = pd.DataFrame(columns=['Category'])
    for num in range (months-1, -1, -1):
        sdate = dates.date.today() + relativedelta(day=1, months= - num)
        fdate = sdate + relativedelta(months=1)
        query = ("SELECT category,sum(value) "
                 "FROM expenses "
                 "WHERE accrual_date >= ? and accrual_date < ? "
                 "GROUP BY category;")
        cur.execute(query, (sdate, fdate))
        result = cur.fetchall()
        label = sdate.strftime('%m/%y')
        tmp = pd.DataFrame(result, columns=['Category', label])
        df = pd.merge(df, tmp, how='outer',
                      left_on='Category', right_on='Category')

    cols = list(df.columns)
    cols.pop(cols.index('Category'))
    cols = ['Category'] + cols
    df = df[cols]
    df.fillna(value=0, inplace=True)
    df["Média"] = df.iloc[:,:-1].mean(axis=1)
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


def brokerage_balance():
    query = ('SELECT custodian,sum(value) '
             'FROM brokerage_transfers '
             'GROUP BY custodian;')
    cur.execute(query)
    result = cur.fetchall()
    brokerage_in = pd.DataFrame(result, columns=['custodian', 'input'])
    query = ('SELECT custodian,sum(value) '
             'FROM investments '
             'GROUP BY custodian;')
    cur.execute(query)
    result = cur.fetchall()
    brokerage_out = pd.DataFrame(result, columns=['custodian', 'output'])

    brokerage = pd.merge(brokerage_in, brokerage_out, how='outer',
                         left_on='custodian', right_on='custodian')
    brokerage.custodian.fillna(value="Não declarado", inplace=True)
    brokerage.rename(columns={'custodian': "Custodiante"}, inplace=True)
    brokerage.fillna(value = 0, inplace=True)
    brokerage["Saldo"] = brokerage.input - brokerage.output
    brokerage.Saldo = brokerage.Saldo.apply(lambda x: math.ceil(100*x)/100)
    brokerage.drop(['input', 'output'], axis=1, inplace=True)
    brokerage = brokerage.sort_values(by="Saldo", ascending=False)

    return brokerage.to_html(classes='brokerage_balance', index=False)
