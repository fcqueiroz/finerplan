from flask import (
    render_template,
    flash,
    Blueprint,
    current_app,
)
from .forms import AddTransactionForm

from finerplan import sql, reports

dashboard_blueprint = Blueprint("dashboard", "finerplan")


@dashboard_blueprint.route('/', methods=['GET', 'POST'])
@dashboard_blueprint.route('/overview', methods=['GET', 'POST'])
def overview():
    form = AddTransactionForm()
    form.cat_expense.choices = sql.generate_categories('expenses')
    form.cat_earning.choices = sql.generate_categories('earnings')
    if form.submit.data:
        if form.transaction.data:
            err = sql.insert_entry(form)
        if err:
            flash("The new entry wasn't inserted correctly. Error {}".format(err))
        else:
            flash("Successfully added new {}".format(form.transaction.data.lower()))
    tables = {'expenses':sql.last_expenses(),
              'earnings':sql.last_earnings(),
              'investments':sql.last_investments()}
    basic_report = reports.basic()
    basic_report['name'] = current_app.config['NAME']
    return render_template('overview.html.jinja', title='Overview', form=form,
                           tables=tables, report=basic_report)


@dashboard_blueprint.route('/expenses', methods=['GET'])
def expenses():
    expenses_table = sql.expenses_table()
    expenses = sql.transactions_table(kind='expenses')
    return render_template('expenses.html.jinja', title='Expenses',
                           tables=expenses_table, expenses=expenses)


@dashboard_blueprint.route('/assets', methods=['GET'])
def assets():
    brokerage_balance = sql.brokerage_balance()

    return render_template('assets.html.jinja', title='Assets',
                           tables=brokerage_balance)
