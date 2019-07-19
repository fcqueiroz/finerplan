# Standard Library
from datetime import datetime, timedelta
import itertools
# 3rd Party Libraries
import pytest
# Local Imports
from app import db
from app.models import User, Transaction, Account
from config import default_account_categories, fundamental_accounts
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

    @pytest.fixture(scope='class')
    def user_with_default_accounts(self, app):
        """Helper function to create user and init default accounts."""
        with app.app_context():
            db.create_all()
            self.create_test_user(db)
            user = User.query.filter_by(username=self.test_user['username']).first()
            user.init_accounts()
            yield user
            db.drop_all()

    def test_init_accounts(self, user_with_default_accounts):
        """Checks that init_accounts creates the default accounts. Depends on config.py"""
        user = user_with_default_accounts

        subaccouts = [t[1] for t in default_account_categories]
        created_accounts = list(itertools.chain(*subaccouts)) + fundamental_accounts
        assert Account.query.filter_by(user_id=user.id).count() == len(created_accounts)

    @pytest.mark.parametrize(('root_node_name', 'min_depth', 'max_depth', 'result'), (
            ('Expenses', None, None, 38),
            ('Expenses', None, 2, 38),
            ('Expenses', None, 1, 10),
            ('Expenses', 1, None, 38),
            ('Housing', None, None, 4)))
    def test_get_descendents(self, user_with_default_accounts, root_node_name, min_depth, max_depth, result):
        """Checks that we can retrieve descendents from a tree node. Depends on config.py"""
        user = user_with_default_accounts

        root = user.accounts.filter_by(name=root_node_name).first()
        children = root.get_descendents(root, min_depth=min_depth, max_depth=max_depth)
        assert children.count() == result

    @pytest.mark.parametrize(('root_node_names', 'result'), (
            ('Expenses', 39),
            ('Income', 6),
            (['Equity', 'Assets', 'Liabilities'], 3)))
    def test_get_subaccounts(self, user_with_default_accounts, root_node_names, result):
        """Tests User method to retrieve subaccounts. Depends on config.py"""
        user = user_with_default_accounts

        subaccounts = user.get_subaccounts(root_names=root_node_names)
        assert len(subaccounts) == result


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
