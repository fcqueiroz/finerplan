import logging

from flask import redirect, render_template, url_for, request, jsonify
from flask_login import current_user, login_required

from finerplan import db
from finerplan.lib.reports import Report
from finerplan.lib.reports import history
from finerplan.models import Transaction, Account

from . import bp
from .forms import AddTransactionForm, AddAccountForm


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/overview', methods=['GET', 'POST'])
@login_required
def overview():
    form = AddTransactionForm()
    # Retrieves all the leaf nodes from user's accounts to use as valid choices.
    user_accounts = [account for account in current_user.accounts if account.is_leaf]
    user_accounts_choices = [(account.id, '') for account in user_accounts]
    form.source_id.choices = user_accounts_choices
    form.destination_id.choices = user_accounts_choices

    if request.method == 'POST':
        form.validate()
        errors = form.errors
        if errors:
            logging.error(errors)
            print(form.data)
    if form.validate_on_submit():
        transaction = {key: form.data[key] for key in form.data.keys()
                       if key not in ['transaction_kind', 'submit', 'csrf_token']}
        # TODO: Rollback transactions if anything goes wrong
        transaction = Transaction(**transaction)
        db.session.add(transaction)
        db.session.commit()

        return redirect(url_for('dashboard.overview'))

    columns = [Transaction.accrual_date, Transaction.description, Transaction.value,
               Transaction.source, Transaction.destination]
    tables = {'transactions': Transaction.query.with_entities(*columns).all()}

    return render_template('overview.html', title='Overview', form=form,
                           tables=tables, report=Report())


def get_group_leaves(user, group):
    major_group = user.accounts.filter_by(group=group)
    return [account for account in major_group if account.is_leaf]


@bp.route('/accounts/<transaction_kind>')
@login_required
def accounts_json(transaction_kind):
    if transaction_kind == 'income':
        source = get_group_leaves(current_user, group='earnings')
        destination = get_group_leaves(current_user, group='equity')
    elif transaction_kind == 'expenses':
        source = get_group_leaves(current_user, group='equity')
        destination = get_group_leaves(current_user, group='expenses')
    else:
        raise ValueError

    data = {'sources': [{'id': account.id, 'name': account.fullname} for account in source],
            'destinations': [{'id': account.id, 'name': account.fullname} for account in destination]}
    return jsonify(data)


@bp.route('/expenses', methods=['GET'])
@login_required
def expenses():
    et1 = history.Expenses()
    return render_template('expenses.html', title='Expenses', tables=et1)


@bp.route('/config/accounts', methods=['GET', 'POST'])
@login_required
def config_accounts():
    form = AddAccountForm()

    if request.method == 'POST':
        form.validate()
        errors = form.errors
        if errors:
            logging.error(errors)
            print(form.data)

    if form.validate_on_submit():
        parent_id = form.data['parent_id']
        parent = Account.query.get(parent_id)
        name = form.data['name']
        Account.create(name, current_user, parent)

        return redirect(url_for('dashboard.config_accounts'))

    return render_template(
        'accounts.html', title='Accounts', accounts=current_user.accounts.all(), form=form)
