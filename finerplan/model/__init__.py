from finerplan import db
from sqlalchemy.orm.exc import NoResultFound

from .account import Account, CreditCard
from .accounting_group import AccountingGroup
from .card import Card
from .report import Report
from .transaction import Transaction
from .user import User

from config import accounting_types, report_names
from data.default import common_accounts


def init_accounting_group():
    """
    Inserts into AccountingGroup the data needed for aplication.
    """
    for group in accounting_types.keys():
        for name in accounting_types[group]:
            try:
                _ = AccountingGroup.query.filter_by(name=name, group=group).one()
            except NoResultFound:
                db.session.add(AccountingGroup(name=name, group=group))
    db.session.commit()


def init_report():
    """
    Inserts into Report the data needed for aplication.
    """
    for group in report_names.keys():
        for name in report_names[group]:
            try:
                _ = Report.query.filter_by(name=name, group=group).one()
            except NoResultFound:
                db.session.add(Report(name=name, group=group))
    db.session.commit()


class GetAccountGroupId(object):
    """
    Finds the id of an account group based on the given group name.

    Offers direct access to the id value or a callable that return the value as needed.
    """

    def __init__(self, name):
        """
        Parameters
        ----------
        name: str
            Group name to be found.
        """
        self.name = name
        self._query = AccountingGroup.query.filter_by(name=self.name)

    @property
    def id(self):
        return self._query.one().id

    def __call__(self):
        return self.id


def add_common_accounts(new_user, data=None, parent_account=None):
    """
    Creates all the common accounts for a given user recursively.

    Parameters
    ----------
    new_user: User
        User object that will have the common account hierarchy added to their account list.
    data: list-like
        Iterable containing a list of accounts to add
    parent_account: Account
        Account object that is the parent of the account being created.
    """
    if data is None:
        data = common_accounts

    for account_data in data:
        account_name = account_data['name']

        if parent_account is None:
            parent_account = account_data['parent']

        try:
            accounting_type = account_data['accounting_type']
        except KeyError:
            accounting_type = parent_account._group.name
        group_id = GetAccountGroupId(name=accounting_type).id

        # Creates the account objects (or retrieves if it already exists)
        try:
            _account = Account.create(name=account_name, group_id=group_id, user=new_user, parent=parent_account)
            db.session.add(_account)
        except NameError:
            _account_list = Account.query.filter_by(name=account_name, group_id=group_id, user_id=new_user.id)
            for _account in _account_list:
                try:
                    depth = parent_account.depth + 1
                except AttributeError:
                    depth = 1

                if _account.depth == depth:
                    break
            else:
                raise AttributeError("The account already exists, but couldn't be found.")
        else:
            db.session.add(_account)
            db.session.commit()

        children_data = account_data.get('children_data', [])
        add_common_accounts(new_user, data=children_data, parent_account=_account)
