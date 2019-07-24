from datetime import date
import locale

from app.sql import SqliteOps
from app.dates import helpers, special_dates as sdates

locale.setlocale(locale.LC_ALL, '')


def basic():
    """Generates basic reports for Overview page.

    Contains credit card and balance current state, based
    on cash date;
    Current month total earnings, expenses and
    savings, based on accrual date;
    Savings Rate of the past 12 months based on accrual accounting.
    """

    sql = SqliteOps()

    SOCM = sdates.start_of_current_month()
    SOM = sdates.start_of_next_month()
    NEXT_PAY = helpers.credit_card_future_payments()
    FOLLOWING_NEXT_PAY = helpers.credit_card_future_payments(1)
    TODAY = date.today()
    M_PROGRESS = helpers.month_progress()

    # This variable holds the user preference for the minimum desired balance
    MIN_TG_BALANCE = 500
    # This variable holds the user preference for maximum expending in luxyry
    LUXURY_BUDGET = 320

    values = (SOCM, SOM)
    query = """expenses WHERE ((? <= accrual_date)
                               and (accrual_date < ?)
                               and (category = 'Restaurantes'
                                    or category = 'Lazer'));"""
    lux_expenses = sql.sum_query(query, values)
    lux_rate = lux_expenses / (LUXURY_BUDGET * M_PROGRESS)

    values = (SOCM, SOM)
    query = 'earnings WHERE ((? <= accrual_date) and (accrual_date < ?));'
    earnings = sql.sum_query(query, values)
    query = 'expenses WHERE ((? <= accrual_date) and (accrual_date < ?));'
    expenses = sql.sum_query(query, values)

    savings = earnings - expenses

    values = (SOM, '-12 month', SOCM)
    query = ('expenses WHERE ((SELECT date(?, ?) <= accrual_date) '
             'and (accrual_date < ?));')
    out_12m = sql.sum_query(query, values)
    query = ('earnings WHERE ((SELECT date(?, ?) <= accrual_date) '
             'and (accrual_date < ?));')
    in_12m = sql.sum_query(query, values)
    if in_12m == 0:
        savings_rate = "Not available"
    else:
        savings_rate = locale.format_string('%.2f %%', 100*(1 - out_12m/in_12m))

    if helpers.credit_state():
        invoice_state = "Closed"
    else:
        invoice_state = "Open"
    query = 'expenses WHERE pay_method="Crédito" and cash_date=?'
    values = (FOLLOWING_NEXT_PAY,)
    next_invoice_value = sql.sum_query(query, values)
    values = (NEXT_PAY,)
    invoice_value = sql.sum_query(query, values)
    query = 'expenses WHERE pay_method="Crédito" and cash_date>=?'
    total_invoice_debt = sql.sum_query(query, values)

    values = (TODAY,)
    query = 'expenses WHERE (cash_date <= ?);'
    t_gasto = sql.sum_query(query, values)
    query = 'earnings WHERE (cash_date <= ?);'
    t_renda = sql.sum_query(query, values)
    query = 'brokerage_transfers WHERE (cash_date <= ?) AND (origin = ?);'
    values = (TODAY, 'Personal')
    t_brokerage_transfers = sql.sum_query(query, values)
    balance = t_renda - t_gasto - t_brokerage_transfers
    free_balance = balance - total_invoice_debt
    sugg_invest = max((balance - invoice_value
                       - sql.ema(kind='double') - MIN_TG_BALANCE), 0)

    return {'earnings': locale.currency(earnings, grouping=True),
            'expenses': locale.currency(expenses, grouping=True),
            'lux_budget': locale.currency(LUXURY_BUDGET - lux_expenses, grouping=True),
            'lux_rate': locale.format_string('%.2f %%', 100*lux_rate),
            'yr_avg_expenses': locale.currency(out_12m / 12, grouping=True),
            'dema': locale.currency(sql.ema(kind='double'), grouping=True),
            'suggested_investment': locale.currency(sugg_invest, grouping=True),
            'savings': locale.currency(savings, grouping=True),
            'savings_rate': savings_rate,
            'balance': locale.currency(balance, grouping=True),
            'free_balance': locale.currency(free_balance, grouping=True),
            'credit_date': NEXT_PAY,
            'credit_value': locale.currency(invoice_value, grouping=True),
            'credit_nvalue': locale.currency(next_invoice_value, grouping=True),
            'credit_state': invoice_state}
