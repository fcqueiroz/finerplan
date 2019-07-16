# Standard Library

# 3rd Party Libraries
from flask_login import current_user
import pytest
# Local Imports
from app.models import User
from tests.test_auth import BasicAuth


class TestUserAccounting(BasicAuth):
    def test_user_has_5_fundamental_accounts(self, app_db):
        """Ensure that whenever a user is created, the 5 fundamental accounts are created as well"""
        self.create_test_user(app_db)

        user = User.query.filter_by(username=self.test_user['username']).first()
        assert user.accounts.count() == 5
