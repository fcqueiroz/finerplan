from config import fundamental_accounts

from .account import Account, CreditCard
from .account_groups import AccountGroups
from .user import User
from .transaction import Transaction


def init_fundamental_accounts(user):
    # Initialize user accounts here
    for account_name in fundamental_accounts:
        try:
            Account.create(
                name=account_name, user=user,
                group_id=AccountGroups.query.filter_by(name=account_name).first().id)
        except NameError:
            pass  # Account is already created
