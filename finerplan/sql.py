import sys
import math
import sqlite3

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
    cur.execute(
        ('SELECT accrual_date,cash_date,description,category,value '
         'FROM earnings '
         'WHERE accrual_date >= ? and accrual_date < ? '
         'ORDER BY accrual_date DESC, id DESC;'),
        (dates.SOCM,dates.SOM))
    return cur.fetchall()

def last_investments():
    """Get all the current month investments"""
    cur.execute(
        ('SELECT accrual_date,cash_date,description,value '
         'FROM assets '
         'WHERE accrual_date >= ? and accrual_date < ? '
         'ORDER BY accrual_date DESC, id DESC;'),
        (dates.SOCM,dates.SOM))
    return cur.fetchall()

def insert_entry(form):
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
                cash = dates.improved_delta(cash, months=1)
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
    """Generate a list of lists
    each inner list contains all the unique category values
    ordened by the most frequent
    """
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
