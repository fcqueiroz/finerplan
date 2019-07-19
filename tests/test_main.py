# Standard Library
from datetime import datetime, timedelta
# 3rd Party Libraries
import pytest
# Local Imports
from app.models import User, Transaction, Account
from tests.test_auth import BasicAuth


class TestUserAccounting(BasicAuth):
    def test_create_account_level_0(self, app_db):
        """Tests that User's create_account method is able to create a
        level-0 account (ie an account without a parent)"""
        self.create_test_user(app_db)
        user = User.query.filter_by(username=self.test_user['username']).first()
        assert user.accounts.count() == 0  # Sanity check

        user.create_account(account_name='Equity')

        assert user.accounts.count() == 1
        account = Account.query.filter_by(user_id=user.id)
        assert account.count() == 1
        assert account.first().path == '/'

    def test_create_account_level_1(self, app_db, child_name='Salary', parent_name='Income'):
        """Tests that User's create_account method is able to create a
        level-1 account (ie a children from a level-0 account)"""
        self.create_test_user(app_db)
        user = User.query.filter_by(username=self.test_user['username']).first()
        user.create_account(account_name=parent_name)

        user.create_account(account_name=child_name, parent_account_name=parent_name)

        account = Account.query.filter_by(user_id=user.id, name=child_name).first()
        assert account.depth == 1
        assert account.path == '/1/'

    def test_init_accounts(self, app_db):
        """Checks that init_accounts creates some accounts"""
        self.create_test_user(app_db)
        user = User.query.filter_by(username=self.test_user['username']).first()
        user.init_accounts()

        assert Account.query.filter_by(user_id=user.id).count() >= 0


class TestTransaction(object):
    @pytest.mark.parametrize(('kind', 'value', 'date', 'description'), [
        ('expenses', 15.80, datetime.now(), "I'm a really long but really useful expense description"),
        ('income', 1200, datetime.now() + timedelta(days=-1), "Regular Salary")
    ])
    def test_insert_transaction(self, app_db, kind, value, date, description):
        assert Transaction.query.count() == 0
        transaction = Transaction(value=value, description=description, accrual_date=date, kind=kind)
        app_db.session.add(transaction)
        assert Transaction.query.count() == 1
