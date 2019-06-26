from flask import flash, redirect, render_template, url_for

from finerplan import app, sql, reports
from finerplan.forms import AddTransactionForm, LoginForm


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect(url_for('overview'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/', methods=['GET', 'POST'])
@app.route('/overview', methods=['GET', 'POST'])
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
    basic_report['name'] = app.config['NAME']
    return render_template('overview.html', title='Overview', form=form,
                           tables=tables, report=basic_report)


@app.route('/expenses', methods=['GET'])
def expenses():
    expenses_table = sql.expenses_table()
    expenses = sql.transactions_table(kind='expenses')
    return render_template('expenses.html', title='Expenses',
                           tables=expenses_table, expenses=expenses)


@app.route('/assets', methods=['GET'])
def assets():
    brokerage_balance = sql.brokerage_balance()

    return render_template('assets.html', title='Assets',
                           tables=brokerage_balance)
