import locale
import sys
from finerplan.core.sql import sum_query, ema
from finerplan.core import dates


def _obtain_user_locale():
    try:
        locale.setlocale(locale.LC_ALL, '')
    except locale.Error:
        sys.exit("Could not obtain system default locale.")


def _assure_valid_locale():
    """Prevent Bug #29 by exiting when locale is C/POSIX."""
    relevant_locale = (
        "LC_MONETARY",
        "LC_NUMERIC",
        "LC_TIME"
    )
    for lc in relevant_locale:
        language_code, encoding = locale.getlocale(category=getattr(locale, lc))
        if language_code is None or encoding is None:
            sys.exit(f"Host system must provide locale but '{lc}' is undefined.")


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
    TODAY, FOLLOWING_NEXT_PAY = sdate['TODAY'], sdate['FOLLOWING_NEXT_PAY']
    M_PROGRESS = sdate['M_PROGRESS']
    # This variable holds the user preference for the minimum desired balance
    MIN_TG_BALANCE = 500
    # This variable holds the user preference for maximum expending in luxyry
    LUXURY_BUDGET = 320

    values = (SOCM, SOM)
    query = """expenses WHERE ((? <= accrual_date)
                               and (accrual_date < ?)
                               and (category = 'Restaurantes'
                                    or category = 'Lazer'));"""
    lux_expenses = sum_query(query, values)
    lux_rate = lux_expenses / (LUXURY_BUDGET * M_PROGRESS)

    values = (SOCM, SOM)
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
    values = (FOLLOWING_NEXT_PAY,)
    next_invoice_value = sum_query(query, values)
    values = (NEXT_PAY,)
    invoice_value = sum_query(query, values)
    query = 'expenses WHERE pay_method="Crédito" and cash_date>=?'
    total_invoice_debt = sum_query(query, values)

    values = (TODAY,)
    query = 'expenses WHERE (cash_date <= ?);'
    t_gasto = sum_query(query, values)
    query = 'earnings WHERE (cash_date <= ?);'
    t_renda = sum_query(query, values)
    query = 'brokerage_transfers WHERE (cash_date <= ?) AND (origin = ?);'
    values = (TODAY, 'Personal')
    t_brokerage_transfers = sum_query(query, values)
    balance = t_renda - t_gasto - t_brokerage_transfers
    free_balance = balance - total_invoice_debt
    sugg_invest = max((balance - invoice_value
                       - ema(kind='double') - MIN_TG_BALANCE), 0)

    return {'earnings': locale.currency(earnings, grouping=True),
            'expenses': locale.currency(expenses, grouping=True),
            'lux_budget': locale.currency(LUXURY_BUDGET - lux_expenses,
                                          grouping=True),
            'lux_rate': locale.format_string('%.2f %%', 100*lux_rate),
            'yr_avg_expenses': locale.currency(out_12m / 12, grouping=True),
            'dema': locale.currency(ema(kind='double'), grouping=True),
            'suggested_investment': locale.currency(sugg_invest, grouping=True),
            'savings': locale.currency(savings, grouping=True),
            'savings_rate': savings_rate,
            'balance': locale.currency(balance, grouping=True),
            'free_balance': locale.currency(free_balance, grouping=True),
            'credit_date': NEXT_PAY,
            'credit_value': locale.currency(invoice_value, grouping=True),
            'credit_nvalue': locale.currency(next_invoice_value, grouping=True),
            'credit_state': invoice_state}


_obtain_user_locale()
_assure_valid_locale()
