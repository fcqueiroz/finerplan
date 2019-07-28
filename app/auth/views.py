from flask import redirect, render_template, url_for, request
from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse

from app.models import User, init_fundamental_accounts

from . import bp
from .forms import LoginForm, RegisterForm


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.overview'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        init_fundamental_accounts(user)

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('dashboard.overview')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.overview'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User.create(username=form.username.data, password=form.password.data, email=form.email.data)
        init_fundamental_accounts(user)

        return redirect(url_for('auth.login'))
    return render_template('register.html', title='Sign Up', form=form)
