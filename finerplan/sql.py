import sys
import math
import sqlite3
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

def last_expenses(num=10):
    """Get last (default=10) entries in expenses database"""
    cur.execute(
        ('SELECT pay_method,accrual_date,cash_date,'
            'description,category_0,value '
         'FROM expenses '
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
         'FROM assets '
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
    cat_0 = form.category_0.data
    cat_1 = "Outras Despesas"
    cat_2 = "Outras Despesas"
    t_val = float(form.value.data.replace(',','.'))
    table = form.transaction.data
    if table == 'expenses':
        query_str = (table+' ( pay_method, accrual_date, cash_date, '
                    'description, category_0, value) Values(?, ?, ?, ?, ?, ?)')
        method = form.pay_method.data
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
    elif (table == 'earnings' or table == 'assets'):
        query_str = (table+' (accrual_date, cash_date, description, '
                    'value) Values(?, ?, ?, ?)')
        query_values = (accrual, cash, descr, t_val)
        cur.execute(('INSERT INTO '+ query_str), query_values)
    else:
        return 2  # Unknown table
    try: con.commit()
    except: return 1  # Failed to commit changes to database

def generate_categories():
    """Generate a tuple containing all the unique categories."""
    query = [('SELECT Category_0,count(Category_0) AS cont FROM expenses '
              'GROUP BY Category_0 ORDER BY cont DESC;'),
             ('SELECT Category_1,count(Category_1) AS cont FROM expenses '
              'GROUP BY Category_1 ORDER BY cont DESC;'),
             ('SELECT Category_2,count(Category_2) AS cont FROM expenses '
              'GROUP BY Category_2 ORDER BY cont DESC;')]
    super_cat=[]
    for q in query:
        cur.execute(q)
        c = [(row[0], row[0]) for row in cur.fetchall()]
        super_cat.append(c)
    return super_cat
