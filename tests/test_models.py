# Standard Library
import itertools
# 3rd Party Libraries
import pytest
# Local Imports
from app.models import User, Transaction, Account
from config import default_account_categories, fundamental_accounts
from tests.conftest import DatabaseMixin
from tests.test_auth import BasicAuth


class TestUserAccounting(DatabaseMixin):
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

    def test_init_accounts(self, user_with_default_accounts):
        """Checks that init_accounts creates the default accounts. Depends on config.py"""
        user = user_with_default_accounts
        subaccouts = [t[1] for t in default_account_categories]
        created_accounts = list(itertools.chain(*subaccouts)) + fundamental_accounts
        assert Account.query.filter_by(user_id=user.id).count() == len(created_accounts)

    @pytest.mark.parametrize(('root_node_name', 'min_depth', 'max_depth', 'inner', 'result'), (
            ('Expenses', None, None, True, 38),
            ('Expenses', None, 2, True, 38),
            ('Expenses', None, 1, True, 10),
            ('Expenses', 1, None, True, 38),
            ('Housing', None, None, True, 4)))
    def test_get_descendents(self, user_with_default_accounts, root_node_name, min_depth, max_depth, inner, result):
        """Checks that we can retrieve descendents from a tree node. Depends on config.py"""
        user = user_with_default_accounts

        root = user.accounts.filter_by(name=root_node_name).first()
        children = root.get_descendents(root, min_depth=min_depth, max_depth=max_depth, inner=inner)
        assert children.count() == result

    @pytest.mark.parametrize(('root_node_names', 'result'), (
            ('Expenses', 29),
            ('Income', 5),
            (['Equity', 'Assets', 'Liabilities'], 3),
            ('Housing', 4),
    ))
    def test_get_subaccounts(self, user_with_default_accounts, root_node_names, result):
        """Tests User method to retrieve subaccounts. Depends on config.py"""
        user = user_with_default_accounts

        subaccounts = user.get_subaccounts(root_names=root_node_names)
        assert len(subaccounts) == result

    @pytest.mark.parametrize('root_node_name',
                             ('Expenses', 'Income', 'Housing'))
    def test_get_subaccounts_fullname(self, user_with_default_accounts, root_node_name):
        """Tests User method to retrieve subaccounts' fullname. Depends on config.py"""
        user = user_with_default_accounts

        subaccounts = user.get_subaccounts(root_names=root_node_name)
        for acc in subaccounts:
            assert root_node_name in acc.fullname
            assert acc.name in acc.fullname


class BasicTransaction(BasicAuth):
    def submit_transation(self, client, transaction=None):
        if transaction is None:
            transaction = self.transaction
            transaction['transaction_kind'] = 'expenses'
        return client.post('/overview', data=dict(**transaction), follow_redirects=True)


class TestTransaction(BasicTransaction):
    def test_insert_transaction_directly_into_db(self, app_db):
        assert Transaction.query.count() == 0
        self.create_transaction(app_db)
        assert Transaction.query.count() == 1

    def test_insert_transaction_through_form(self, client, user_with_default_accounts):
        assert Transaction.query.count() == 0
        user = user_with_default_accounts
        with client:
            self.login(client)
            self.submit_transation(client)

        assert Transaction.query.count() == 1
