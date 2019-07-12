from flask import flash, redirect, render_template, url_for, Blueprint, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app import reports
from app import db
from app.forms import AddTransactionForm, LoginForm, RegisterForm
from app.sql import SqliteOps
from app.models import User
from config import UserInfo

simple_page = Blueprint('simple_page', __name__, template_folder='templates')
sql = SqliteOps()


@simple_page.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('simple_page.overview'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None:
            flash('Invalid username')
            next_page = url_for('simple_page.login')
        elif not user.check_password(form.password.data):
            flash('Invalid password')
            next_page = url_for('simple_page.login')
        else:
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
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('simple_page.login'))
    return render_template('register.html', title='Sign Up', form=form)


@simple_page.route('/', methods=['GET', 'POST'])
@simple_page.route('/overview', methods=['GET', 'POST'])
@login_required
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
@login_required
def expenses():
    et1 = sql.expenses_table()
    et2 = sql.transactions_table(kind='expenses')
    return render_template('expenses.html', title='Expenses',
                           tables=et1, expenses=et2)


@simple_page.route('/assets', methods=['GET'])
@login_required
def assets():
    balance = sql.brokerage_balance()

    return render_template('assets.html', title='Assets',
                           tables=balance)
