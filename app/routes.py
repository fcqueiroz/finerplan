from flask import flash, redirect, render_template, url_for, Blueprint

from app import reports
from app.forms import AddTransactionForm, LoginForm
from app.sql import SqliteOps
from config import UserInfo

simple_page = Blueprint('simple_page', __name__, template_folder='templates')
sql = SqliteOps()


@simple_page.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect(url_for('overview'))
    return render_template('login.html', title='Sign In', form=form)


@simple_page.route('/', methods=['GET', 'POST'])
@simple_page.route('/overview', methods=['GET', 'POST'])
def overview():
    form = AddTransactionForm()
    if form.submit.data:
        if form.transaction.data:
            err = sql.insert_entry(form)
        if err:
            flash("The new entry wasn't inserted correctly. Error {}".format(err))
        else:
            flash("Successfully added new {}".format(form.transaction.data.lower()))
    tables = {'expenses': sql.last_expenses(),
              'earnings': sql.last_earnings(),
              'investments': sql.last_investments()}
    basic_report = reports.basic()
    basic_report['name'] = UserInfo.NAME
    return render_template('overview.html', title='Overview', form=form,
                           tables=tables, report=basic_report)


@simple_page.route('/expenses', methods=['GET'])
def expenses():
    et1 = sql.expenses_table()
    et2 = sql.transactions_table(kind='expenses')
    return render_template('expenses.html', title='Expenses',
                           tables=et1, expenses=et2)


@simple_page.route('/assets', methods=['GET'])
def assets():
    balance = sql.brokerage_balance()

    return render_template('assets.html', title='Assets',
                           tables=balance)
