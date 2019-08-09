import logging

from flask import redirect, render_template, url_for, request, jsonify
from flask_login import current_user, login_required
from sqlalchemy import or_

from finerplan.model import Transaction, Account, CreditCard, AccountingGroup, Card, Report, add_common_accounts
from finerplan.reports import ReportCard, history

from . import bp
from .forms import AddTransactionForm, AddAccountForm, AddReportCardForm


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

    cards = [ReportCard(card=c) for c in current_user.cards]

    return render_template('explore/overview.html', title='Overview', form=form,
                           tables=tables, cards=cards)


@bp.route('/accounts/<transaction_kind>')
@login_required
def accounts_json(transaction_kind):
    def get_group_leaves(user, *group_names):
        group_names_filter = [(name == AccountingGroup.group) for name in group_names]
        accounts = user.accounts.join(Account._group).filter(or_(*group_names_filter))
        result = [account for account in accounts if account.is_leaf]
        return result

    if transaction_kind == 'income':
        source = get_group_leaves(current_user, 'Income')
        destination = get_group_leaves(current_user, 'Equity', 'Asset', 'Liability')
    elif transaction_kind == 'expenses':
        source = get_group_leaves(current_user, 'Equity', 'Asset', 'Liability')
        destination = get_group_leaves(current_user, 'Expense')
    else:
        raise ValueError

    data = {'sources': [{'id': account.id, 'name': account.fullname, 'type': account.type} for account in source],
            'destinations': [{'id': account.id, 'name': account.fullname} for account in destination]}
    return jsonify(data)


@bp.route('/accounts/create_common', methods=['POST'])
@login_required
def accounts_create_common():
    add_common_accounts(current_user)
    return redirect(url_for('dashboard.accounts_list'))


@bp.route('/expenses', methods=['GET'])
@login_required
def expenses():
    et1 = history.Expenses()
    return render_template('explore/expenses.html', title='Expenses', tables=et1)


@bp.route('/config/accounts', methods=['GET'])
@login_required
def accounts_list():
    form = AddAccountForm()
    group_choices = [(group.id, group.name) for group in AccountingGroup.query.all()]
    # TODO Dynamically populate this based on parent account group
    form.group_id.choices = group_choices

    return render_template(
        'config/accounts.html', title='Accounts', accounts=current_user.accounts.all(), form=form)


@bp.route('/config/accounts', methods=['POST'])
@login_required
def accounts_create():
    form = AddAccountForm()
    group_choices = [(group.id, group.name) for group in AccountingGroup.query.all()]
    # TODO Dynamically populate this based on parent account group
    form.group_id.choices = group_choices

    form.validate()
    errors = form.errors
    if errors:
        logging.error(errors)
        print(form.data)

    # Post process form data
    parent_id = request.form.get('parent_id')
    if parent_id:
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

        if AccountingGroup.query.get(group_id).name == 'Credit Card':
            CreditCard.create(
                closing=form.data['closing'],
                payment=form.data['payment'],
                **account_data)
        else:
            Account.create(**account_data)

        return redirect(url_for('dashboard.accounts_list'))

    return render_template(
        'config/accounts.html', title='Accounts', accounts=current_user.accounts.all(), form=form)


@bp.route('/config/accounts/<int:account_id>', methods=['GET', 'POST'])
@login_required
def edit_accounts(account_id):
    pass


@bp.route('/config/reports', methods=['GET'])
@login_required
def reports_list():
    form = AddReportCardForm()
    cards = current_user.cards.all()

    return render_template(
        'config/reports.html', title='Reports', cards=cards, form=form)


@bp.route('/config/reports', methods=['POST'])
@login_required
def reports_create():
    form = AddReportCardForm()
    cards = current_user.cards.all()

    form.validate()
    errors = form.errors
    if errors:
        logging.error(errors)
        print(form.data)

    if form.validate_on_submit():
        card = Card.create(user=current_user, name=form.data.pop('name'))
        Report.assign_to(card, **form.data)

        return redirect(url_for('dashboard.reports_list'))

    return render_template(
        'config/reports.html', title='Reports', cards=cards, form=form)
