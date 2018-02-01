import locale
locale.setlocale(locale.LC_ALL, '')
from finerplan.sql import sum_query

from finerplan import dates

def basic():
    """Generates basic reports for Overview page.

    Contains credit card and balance current state, based
    on cash date;
    Current month total earnings, expenses and
    savings, based on accrual date;
    Savings Rate of the past 12 months based on accrual accounting.
    """

    sdate = dates.sdate()
    SOCM, SOM, NEXT_PAY = sdate['SOCM'], sdate['SOM'], sdate['NEXT_PAY']
    TODAY = sdate['TODAY']

    values = (SOCM, SOM,)
    query = 'earnings WHERE ((? <= accrual_date) and (accrual_date < ?));'
    earnings = sum_query(query, values)
    query = 'expenses WHERE ((? <= accrual_date) and (accrual_date < ?));'
    expenses = sum_query(query, values)

    savings = earnings - expenses

    values = (SOM, '-12 month', SOCM)
    query = ('expenses WHERE ((SELECT date(?, ?) <= accrual_date) '
            'and (accrual_date < ?));')
    out_12m = sum_query(query, values)
    query = ('earnings WHERE ((SELECT date(?, ?) <= accrual_date) '
            'and (accrual_date < ?));')
    in_12m = sum_query(query, values)
    if in_12m == 0:
        savings_rate = "Not available"
    else:
        savings_rate = locale.format_string('%.2f %%', 100*(1 - out_12m/in_12m))

    if dates.credit_state():
        invoice_state = "Closed"
    else:
        invoice_state = "Open"
    query = 'expenses WHERE pay_method="Crédito" and cash_date=?'
    values = (NEXT_PAY,)
    invoice_value = sum_query(query, values)

    values = (TODAY,)
    query = 'expenses WHERE (cash_date <= ?);'
    t_gasto = sum_query(query, values)
    query = 'earnings WHERE (cash_date <= ?);'
    t_renda = sum_query(query, values)
    query = 'assets WHERE (cash_date <= ?);'
    t_assets = sum_query(query, values)
    balance = t_renda - t_gasto - t_assets

    return {'earnings': locale.currency(earnings, grouping=True),
            'expenses': locale.currency(expenses, grouping=True),
            'savings': locale.currency(savings, grouping=True),
            'savings_rate': savings_rate,
            'balance': locale.currency(balance, grouping=True),
            'credit_date': NEXT_PAY,
            'credit_value': locale.currency(invoice_value, grouping=True),
            'credit_state': invoice_state}
