import sqlite3 #as lite
#con = lite.connect('/home/fernanda/Git/finerplan/finerplan/finerplan.db',  check_same_thread=False)
#cur = con.cursor()
#from finerplan.finerplan import connect_db
from finerplan.finerplan import app

import sys
import locale
locale.setlocale(locale.LC_ALL, '')
from datetime import date
from datetime import datetime

def next_month(dtDateTime, start=False):
    from datetime import timedelta
    # Returns the last day of the month for a given date by default
    # If start=True returns the first day of the next month for the given date
    dMonth = dtDateTime.month + 1
    if dMonth == 13:
        dMonth = 1
        dYear = dtDateTime.year + 1
    else:
        dYear = dtDateTime.year
    sonm = date(dYear, dMonth, 1)
    if start:
        return sonm
    else:
        return sonm - timedelta(days=1)

# Specific dates in string format
# socm: Start Of Current Month
# eom: End Of [current] Month
# som: Start Of [next] Month
s_socm = date(date.today().year,date.today().month,1).strftime("%Y-%m-%d")
s_eom = next_month(date.today()).strftime("%d/%b/%Y")
s_som = next_month(date.today(), start=True).strftime("%Y-%m-%d")

#Connects to the specific database. Creates the tables if they don't exist.
con = sqlite3.connect(app.config['DATABASE'],  check_same_thread=False)
#con.row_factory = sqlite3.Row
with app.open_resource('schema.sql', mode='r') as f:
    con.cursor().executescript(f.read())
con.commit()
cur = con.cursor()

# Return expected balance for the end of the current month
def balance_eom(local=False):
    cur.execute("SELECT sum(Value) FROM expenses WHERE (cash_date < ?);", (s_som,))
    t_gasto = cur.fetchone()[0]
    cur.execute("SELECT sum(Value) FROM earnings WHERE (cash_date < ?);", (s_som,))
    t_renda = cur.fetchone()[0]
    cur.execute("SELECT sum(Value) FROM assets WHERE (cash_date < ?);", (s_som,))
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
    cur.execute("SELECT sum(Value) FROM earnings WHERE ((? <= accrual_date) and (accrual_date < ?));", (s_socm, s_som,))
    earnings = cur.fetchone()[0]
    if not isinstance(earnings, (int, float)):
        earnings = 0
    if local:
        return locale.currency(earnings, grouping=True)
    else:
        return earnings

# Get current month total expenses
def expenses_ocm(local=False):
    cur.execute("SELECT sum(Value) FROM expenses WHERE ((? <= accrual_date) and (accrual_date < ?));", (s_socm,s_som))
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

# Get last 12 months savings rate
def savings_rate():
    cur.execute("SELECT sum(Value) FROM earnings WHERE ((SELECT date(?, '-12 month') <= accrual_date) and (accrual_date < ?));", (s_som, s_socm))
    receita_12m = cur.fetchone()[0]
    if (not isinstance(receita_12m, (int, float)) or receita_12m ==0):
        return "No earnings in the last 12 months"
    cur.execute("SELECT sum(Value) FROM expenses WHERE ((SELECT date(?, '-12 month') <= accrual_date) and (accrual_date < ?));", (s_som, s_socm))
    gasto_12m = cur.fetchone()[0]
    if not isinstance(gasto_12m, (int, float)):
        gasto_12m = 0
    return locale.format_string('%.2f %%', 100*(1 - gasto_12m/receita_12m))

# Get last 'num' (default=10) entries in expenses database
def last_expenses(num=10):
    cur.execute("SELECT id,accrual_date,cash_date,description,category_0,value FROM expenses WHERE id > ((select count(*) from expenses) - ?);", (num,))
    return cur.fetchall()
    
def insert_expense(new_entry):
    # As a temporary solution for simplicity, all the new entries receive category_1 = 'Outras Despesas' and category_2 = 'Outras Despesas'
    # As a temporary solution for simplicity, the accrual_date and cash_date are the same
    cur.execute("INSERT INTO expenses (accrual_date, cash_date, description, category_0, category_1, category_2, value) Values(?, ?, ?, ?, 'Outras Despesas', 'Outras Despesas', ?)", (new_entry[1], new_entry[1], new_entry[2], new_entry[3], new_entry[4]))
    con.commit()

# Generate a list of lists, where each inner list curtains all the unique category values ordened by the most frequent
def generate_categories():
    query = ["SELECT Category_0,count(Category_0) AS cont FROM expenses GROUP BY Category_0 ORDER BY cont DESC",
             "SELECT Category_1,count(Category_1) AS cont FROM expenses GROUP BY Category_1 ORDER BY cont DESC",
             "SELECT Category_2,count(Category_2) AS cont FROM expenses GROUP BY Category_2 ORDER BY cont DESC",]
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
    
