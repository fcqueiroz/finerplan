from app.models import Account


def test_user_init_accounts(test_user):
    user = test_user
    assert user.accounts.count() == 0  # Sanity check

    user.init_accounts()
    assert user.accounts.count() == 3


def test_user_fundamental_account_attribute(test_user):
    """Tests that the fundamental accounts are available as attributes of the User instance."""
    user = test_user
    user.init_accounts()

    fundamental_account = ['Equity', 'Earnings', 'Expenses']
    for account in fundamental_account:
        assert isinstance(getattr(user, account.lower()), Account)
        assert getattr(user, account.lower()).name == account
