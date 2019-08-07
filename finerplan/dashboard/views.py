import logging

from flask import redirect, render_template, url_for, request, jsonify
from flask_login import current_user, login_required

from finerplan.dashboard.reports import Report, history
from finerplan.model import Transaction, Account, CreditCard, AccountGroups

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
        _ = Transaction.create(**transaction)

        return redirect(url_for('dashboard.overview'))

    tables = {'transactions': [
        (t.accrual_date, t.description, t.value, t.source.name, t.destination.name)
        for t in Transaction.query.all()]}

    return render_template('explore/overview.html', title='Overview', form=form,
                           tables=tables, report=Report())


def get_group_leaves(user, group):
    _group = AccountGroups.query.filter_by(name=group).first()
    major_group = user.accounts.filter_by(group_id=_group.id)
    return [account for account in major_group if account.is_leaf]


@bp.route('/accounts/<transaction_kind>')
@login_required
def accounts_json(transaction_kind):
    if transaction_kind == 'income':
        source = get_group_leaves(current_user, group='Income')
        destination = get_group_leaves(current_user, group='Equity')
    elif transaction_kind == 'expenses':
        source = get_group_leaves(current_user, group='Equity')
        destination = get_group_leaves(current_user, group='Expenses')
    else:
        raise ValueError

    data = {'sources': [{'id': account.id, 'name': account.fullname} for account in source],
            'destinations': [{'id': account.id, 'name': account.fullname} for account in destination]}
    return jsonify(data)


@bp.route('/expenses', methods=['GET'])
@login_required
def expenses():
    et1 = history.Expenses()
    return render_template('explore/expenses.html', title='Expenses', tables=et1)


@bp.route('/config/accounts', methods=['GET'])
@login_required
def config_accounts_list():
    form = AddAccountForm()
    group_choices = [(group.id, group.name) for group in AccountGroups.query.all()]
    # TODO Dynamically populate this based on parent account group
    form.group_id.choices = group_choices

    return render_template(
        'config/accounts.html', title='Accounts', accounts=current_user.accounts.all(), form=form)


@bp.route('/config/accounts', methods=['POST'])
@login_required
def config_accounts_create():
    form = AddAccountForm()
    group_choices = [(group.id, group.name) for group in AccountGroups.query.all()]
    # TODO Dynamically populate this based on parent account group
    form.group_id.choices = group_choices

    form.validate()
    errors = form.errors
    if errors:
        logging.error(errors)
        print(form.data)

    # Post process form data
    parent_id = request.form.get('parent_id')
    if parent_id is not None:
        parent = Account.query.get(int(parent_id))
        assert parent.user_id == current_user.id
    else:
        parent = None
    group_id = form.data['group_id']

    if form.validate_on_submit():
        account_data = dict(
            name=form.data['name'],
            user=current_user,
            group_id=group_id,
            parent=parent)

        if AccountGroups.query.get(group_id).name == 'Credit Card':
            CreditCard.create(
                closing=form.data['closing'],
                payment=form.data['payment'],
                **account_data)
        else:
            Account.create(**account_data)

        return redirect(url_for('dashboard.config_accounts_list'))

    return render_template(
        'config/accounts.html', title='Accounts', accounts=current_user.accounts.all(), form=form)


@bp.route('/config/accounts/<int:account_id>', methods=['GET', 'POST'])
@login_required
def edit_accounts(account_id):
    pass
