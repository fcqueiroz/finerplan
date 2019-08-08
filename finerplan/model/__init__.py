from finerplan import db

from .account import Account, CreditCard
from .account_groups import AccountGroups
from .card import Card, Report
from .user import User
from .transaction import Transaction

from config import fundamental_accounts, account_groups_list, report_names


def init_fundamental_accounts(user):
    # Initialize user accounts here
    for account_name in fundamental_accounts:
        try:
            Account.create(
                name=account_name, user=user,
                group_id=AccountGroups.query.filter_by(name=account_name).first().id)
        except NameError:
            pass  # Account is already created


def init_account_groups():
    """
    Inserts into AccountGroups the data needed for aplication.
    """
    for group_name in account_groups_list:
        result = AccountGroups.query.filter_by(name=group_name).first()
        if result is None:
            db.session.add(AccountGroups(name=group_name))
    db.session.commit()


def init_reports():
    """
    Inserts into Report the data needed for aplication.
    """
    for report in report_names['Information']:
        result = Report.query.filter_by(name=report).first()
        if result is None:
            db.session.add(Report(name=report))
    db.session.commit()
