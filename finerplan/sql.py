import sys
import math
import sqlite3
import pandas as pd
from dateutil.relativedelta import *

from .finerplan import app, form_words
from finerplan import dates

con = sqlite3.connect(app.config['DATABASE'],  check_same_thread=False)
#con.row_factory = sqlite3.Row
cur = con.cursor()

def sum_query(query_str, query_values):
    cur.execute('SELECT sum(value) FROM ' + query_str, query_values)
    result =  cur.fetchone()[0]
    if not isinstance(result, (int, float)):
        result = 0
    return result

def ema(alpha=0.15):
    sdate = dates.sdate()
    SOCM = sdate['SOCM']
    query = 'select accrual_date from expenses order by accrual_date;'
    cur.execute(query)
    oldest_date = cur.fetchone()[0]
    if not isinstance(oldest_date, (str,)):
        return 0
    month_start = dates.date_converter(oldest_date)
    month_ending = month_start + relativedelta(day=31)

    cur.execute('SELECT sum(value) FROM expenses '
                'WHERE accrual_date>=? AND accrual_date <=?;',
                (month_start, month_ending))
    mov_avg = cur.fetchone()[0]
    if not isinstance(mov_avg, (int, float)):
        return 0
    while (True):
        month_start = month_ending + relativedelta(days=1)
        month_ending = month_start + relativedelta(day=31)

        cur.execute('SELECT sum(value) FROM expenses '
                    'WHERE accrual_date>=? AND accrual_date <=?;',
                    (month_start, month_ending))
        result = cur.fetchone()[0]
        if not isinstance(result, (int, float)):
            return mov_avg
        else:
            if month_start == SOCM:
                return mov_avg
                #result = result * ((month_ending - month_start).days + 1) / (date.today() - month_start).days
            mov_avg = alpha*result + (1-alpha)*mov_avg

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
        SOCM = sdate['SOCM'].strftime(dates.__MODEL)
        SOM = sdate['SOM'].strftime(dates.__MODEL)
        data_range = ('WHERE accrual_date >= "' + SOCM +
                      '" and accrual_date < "' + SOM + '" ')
    else:
        data_range = ''

    if kind == 'expenses':
        query = ('SELECT pay_method,accrual_date,'
                     'description,category,sum(value) '
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
    try: con.commit()
    except: return 1  # Failed to commit changes to database

def generate_categories(table='expenses'):
    """Generate a tuple containing all the unique categories."""

    # For future: Option to return a default list of categories
    # This is specially important when a user is initianing a database
    if table == 'expenses':
        query = ('SELECT category,count(category) AS cont FROM expenses '
                 'GROUP BY category ORDER BY cont DESC;')
    elif table == 'earnings':
        query = ('SELECT Category,count(Category) AS cont FROM earnings '
                 'GROUP BY Category ORDER BY cont DESC;')

    cur.execute(query)
    super_cat = [(row[0], row[0]) for row in cur.fetchall()]

    return super_cat

def expenses_table(months=6):
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

    df.fillna(value=0, inplace=True)
    df["Soma"] = df.sum(axis=1)
    df = df.sort_values(by="Soma", ascending=False)

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
    brokerage.drop(['input', 'output'], axis=1, inplace=True)
    brokerage = brokerage.sort_values(by="Saldo", ascending=False)

    return brokerage.to_html(classes='brokerage_balance', index=False)
