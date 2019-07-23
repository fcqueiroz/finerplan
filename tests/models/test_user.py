

def test_user_init_accounts(test_user):
    user = test_user
    assert user.accounts.count() == 0  # Sanity check

    user.init_accounts()
    assert user.accounts.count() == 4
