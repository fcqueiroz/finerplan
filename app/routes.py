import logging
from flask import redirect, render_template, url_for, Blueprint, request, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app.reports import Report
from app import db
from app.forms import AddTransactionForm, LoginForm, RegisterForm
from app.sql import SqliteOps
from app.models import User, Transaction

simple_page = Blueprint('simple_page', __name__, template_folder='templates')
sql = SqliteOps()


@simple_page.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('simple_page.overview'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('simple_page.overview')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@simple_page.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('simple_page.login'))


@simple_page.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('simple_page.overview'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, password=form.password.data, email=form.email.data)
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('simple_page.login'))
    return render_template('register.html', title='Sign Up', form=form)


@simple_page.route('/', methods=['GET', 'POST'])
@simple_page.route('/overview', methods=['GET', 'POST'])
@login_required
def overview():
    form = AddTransactionForm()
    form.transaction_kind.choices = [(kind.lower(), kind) for kind in ['Income', 'Expenses']]

    # Todo Fill the choices using the same accounts view that produces the json
    # Retrieves only the leaf nodes from user's accounts
    user_accounts = [account for account in current_user.accounts if account.is_leaf]
    user_accounts_choices = [(account.id, '') for account in user_accounts]
    form.account_source.choices = user_accounts_choices
    form.account_destination.choices = user_accounts_choices

    if request.method == 'POST':
        form.validate()
        errors = form.errors
        if errors:
            logging.error(errors)
            print(form.data)
    if form.validate_on_submit():
        transaction = {key: form.data[key] for key in form.data.keys()
                       if key not in ['transaction_kind', 'submit', 'csrf_token']}
        transaction = Transaction(**transaction)
        db.session.add(transaction)
        db.session.commit()
        return redirect(url_for('simple_page.overview'))

    columns = [Transaction.accrual_date, Transaction.description, Transaction.value,
               Transaction.source, Transaction.destination]
    tables = {'transactions': Transaction.query.with_entities(*columns).all()}

    return render_template('overview.html', title='Overview', form=form,
                           tables=tables, report=Report())


@simple_page.route('/accounts/<transaction_kind>')
@login_required
def accounts(transaction_kind):
    # TODO Test this view!

    leaves = dict()
    for name in ['equity', 'expenses', 'earnings']:
        leaves[name] = [account for account in getattr(current_user, name).descendents() if account.is_leaf]

    if transaction_kind == 'income':
        source = leaves['earnings']
        destination = leaves['equity']
    elif transaction_kind == 'expenses':
        source = leaves['equity']
        destination = leaves['expenses']
    else:
        raise ValueError

    data = {'sources': [{'id': account.id, 'name': account.fullname} for account in source],
            'destinations': [{'id': account.id, 'name': account.fullname} for account in destination]}
    return jsonify(data)


@simple_page.route('/expenses', methods=['GET'])
@login_required
def expenses():
    et1 = sql.expenses_table()
    return render_template('expenses.html', title='Expenses', tables=et1)
