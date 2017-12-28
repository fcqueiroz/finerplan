import sqlite3 #as lite
from .finerplan import app
import sys
import locale
locale.setlocale(locale.LC_ALL, '')
import math
from finerplan import dates

# Connects to the specific database
con = sqlite3.connect(app.config['DATABASE'],  check_same_thread=False)
#con.row_factory = sqlite3.Row
cur = con.cursor()

# Return expected balance for the end of the current month
def balance_eom(local=False):
    cur.execute('SELECT sum(Value) FROM expenses WHERE (cash_date < ?);', (dates.s_som,))
    t_gasto = cur.fetchone()[0]
    cur.execute('SELECT sum(Value) FROM earnings WHERE (cash_date < ?);', (dates.s_som,))
    t_renda = cur.fetchone()[0]
    cur.execute('SELECT sum(Value) FROM assets WHERE (cash_date < ?);', (dates.s_som,))
    t_assets = cur.fetchone()[0]
    if not isinstance(t_gasto, (int, float)):
        t_gasto = 0
    if not isinstance(t_renda, (int, float)):
        t_renda = 0
    if not isinstance(t_assets, (int, float)):
        t_assets = 0
    if local:
        return locale.currency(t_renda - t_gasto - t_assets, grouping=True)
    else:
        return t_renda - t_gasto - t_assets

# Get current month total earnings
def income_ocm(local=False):
    cur.execute('SELECT sum(Value) FROM earnings WHERE ((? <= accrual_date) and (accrual_date < ?));', (dates.s_socm, dates.s_som,))
    earnings = cur.fetchone()[0]
    if not isinstance(earnings, (int, float)):
        earnings = 0
    if local:
        return locale.currency(earnings, grouping=True)
    else:
        return earnings

# Get current month total expenses
def expenses_ocm(local=False):
    cur.execute('SELECT sum(Value) FROM expenses WHERE ((? <= accrual_date) and (accrual_date < ?));', (dates.s_socm,dates.s_som))
    expenses = cur.fetchone()[0]
    if not isinstance(expenses, (int, float)):
        expenses = 0
    if local:
        return locale.currency(expenses, grouping=True)
    else:
        return expenses

# Get current month total savings
def savings_ocm(local=False):
    if local:
        return locale.currency(income_ocm() - expenses_ocm(), grouping=True)
    else:
        return income_ocm() - expenses_ocm()

# Generates information about next credit card invoice payment
def credit_payment(local=False):
    if (dates.tday.day > app.config['CREDIT_CLOSING']) and (dates.tday.day <= app.config['CREDIT_PAYMENT']):
        invoice_state = "Closed"
    else:
        invoice_state = "Open"
    cur.execute('SELECT SUM(value) FROM expenses WHERE pay_method="Crédito" and cash_date=?',(dates.next_pay.strftime(dates.model),))
    invoice_value = cur.fetchone()[0]
    if not isinstance(invoice_value, (int, float)):
        invoice_value = 0
    if local:
        return {'date': dates.next_pay.strftime(dates.model), 'state': invoice_state, 'value': locale.currency(invoice_value, grouping=True)}
    else:
        return {'date': dates.next_pay.strftime(dates.model), 'state': invoice_state, 'value': invoice_value}

# Get last 12 months savings rate
def savings_rate():
    cur.execute('SELECT sum(Value) FROM earnings WHERE ((SELECT date(?, ?) <= accrual_date) and (accrual_date < ?));', (dates.s_som, '-12 month', dates.s_socm))
    receita_12m = cur.fetchone()[0]
    if (not isinstance(receita_12m, (int, float)) or receita_12m ==0):
        return "No earnings in the last 12 months"
    cur.execute('SELECT sum(Value) FROM expenses WHERE ((SELECT date(?, ?) <= accrual_date) and (accrual_date < ?));', (dates.s_som, '-12 month', dates.s_socm))
    gasto_12m = cur.fetchone()[0]
    if not isinstance(gasto_12m, (int, float)):
        gasto_12m = 0
    return locale.format_string('%.2f %%', 100*(1 - gasto_12m/receita_12m))

# Get last (default=10) entries in expenses database
def last_expenses(num=10):
    cur.execute('SELECT pay_method,accrual_date,cash_date,description,category_0,value FROM expenses ORDER BY accrual_date DESC, id DESC LIMIT ?;', (num,))
    return cur.fetchall()
    
# Get all the current month earnings
def last_earnings():
    cur.execute('SELECT accrual_date,cash_date,description,category,value FROM earnings WHERE accrual_date >= ? and accrual_date < ? ORDER BY accrual_date DESC, id DESC;', (dates.s_socm,dates.s_som))
    return cur.fetchall()

# Get all the current month investments
def last_investments():
    cur.execute('SELECT accrual_date,cash_date,description,value FROM assets WHERE accrual_date >= ? and accrual_date < ? ORDER BY accrual_date DESC, id DESC;', (dates.s_socm,dates.s_som))
    return cur.fetchall()
    
def insert_expense(form):
    # As a temporary solution for simplicity, all the new entries receive category_1 = 'Outras Despesas' and category_2 = 'Outras Despesas'
    method = form.pay_method.data.split(',')[0]
    try: installments = int(form.pay_method.data.split(',')[1])
    except: installments = 1
    s_accrual = form.date.data
    accrual = datetime.strptime(s_accrual,dates.model).date()
    descr = form.description.data
    cat_0 = form.category_0.data
    cat_1 = "Outras Despesas"
    cat_2 = "Outras Despesas"
    t_value = float(form.value.data.replace(',','.'))
    if method=="Dinheiro":
        cur.execute('INSERT INTO expenses (pay_method, accrual_date, cash_date, description, category_0, category_1, category_2, value) Values(?, ?, ?, ?, ?, ?, ?, ?)', (method, s_accrual, s_accrual, descr, cat_0, cat_1, cat_2, t_value))
    elif method == "Crédito":
        val_installment = round(((100*t_value) // installments + (100*t_value) % installments) /100,2)
        cash_date = date(accrual.year, accrual.month, app.config['CREDIT_PAYMENT'])
        if accrual.day > app.config['CREDIT_CLOSING']:
            cash_date = dates.months_delta(cash_date,1)
        cur.execute('INSERT INTO expenses (pay_method, accrual_date, cash_date, description, category_0, category_1, category_2, value) Values(?, ?, ?, ?, ?, ?, ?, ?)', (method, s_accrual, cash_date.strftime(dates.model), descr, cat_0, cat_1, cat_2, val_installment))
        if installments > 1:
            val_installment = round(((100*t_value) // installments) / 100,2)
            for i in range(1, installments):
                cash_date = dates.months_delta(cash_date, 1)
                cur.execute('INSERT INTO expenses (pay_method, accrual_date, cash_date, description, category_0, category_1, category_2, value) Values(?, ?, ?, ?, ?, ?, ?, ?)', (method, s_accrual, cash_date.strftime(dates.model), descr, cat_0, cat_1, cat_2, val_installment))
    elif method == "Terceiros":
        cur.execute('INSERT INTO earnings (accrual_date, cash_date, description, category, value) Values(?, ?, ?, ?, ?)', (s_accrual, s_accrual, descr, "Subsídio", t_value))
        cur.execute('INSERT INTO expenses (pay_method, accrual_date, cash_date, description, category_0, category_1, category_2, value) Values(?, ?, ?, ?, ?, ?, ?, ?)', (method, s_accrual, s_accrual, descr, cat_0, cat_1, cat_2, t_value))
    else:
        return 1
    try: con.commit()
    except: return 2

def insert_earning(form):
    cur.execute('INSERT INTO earnings (accrual_date, cash_date, description, category, value) Values(?, ?, ?, ?, ?)', (form.date.data, form.date.data, form.description.data, form.category_0.data, float(form.value.data.replace(',','.'))))
    try: con.commit()
    except: return 2

def insert_investment(form):
    cur.execute('INSERT INTO assets (accrual_date, cash_date, description, category, value) Values(?, ?, ?, ?, ?)', (form.date.data, form.date.data, form.description.data, form.category_0.data, float(form.value.data.replace(',','.'))))
    try: con.commit()
    except: return 2

# Generate a list of lists, where each inner list contains all the unique category values ordened by the most frequent
def generate_categories():
    query = ['SELECT Category_0,count(Category_0) AS cont FROM expenses GROUP BY Category_0 ORDER BY cont DESC',
             'SELECT Category_1,count(Category_1) AS cont FROM expenses GROUP BY Category_1 ORDER BY cont DESC',
             'SELECT Category_2,count(Category_2) AS cont FROM expenses GROUP BY Category_2 ORDER BY cont DESC',]
    super_cat=[]
    for q in query:
        cur.execute(q)
        c = []
        i = 1
        for row in cur.fetchall():
            c.append((i, row[0]))
            i +=1
        super_cat.append(c)
    return super_cat
    
