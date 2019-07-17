# Standard Library
from datetime import datetime, timedelta
# 3rd Party Libraries
import pytest
# Local Imports
from app.models import User, Transaction
from tests.test_auth import BasicAuth


class TestUserAccounting(BasicAuth):
    def test_user_has_5_fundamental_accounts(self, app_db):
        """Ensure that whenever a user is created, the 5 fundamental accounts are created as well"""
        self.create_test_user(app_db)

        user = User.query.filter_by(username=self.test_user['username']).first()
        assert user.accounts.count() == 5


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
