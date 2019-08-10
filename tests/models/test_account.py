import pytest

from finerplan.model import Account, GetAccountGroupId


def test_create_account_refuses_duplicated_fullname(test_user):
    """
    Tests that method to create an account linked to a user does
    not allow the creation of two accounts with the same fullname.
    """
    _ = Account.create(
        name='Equity', user=test_user, parent=None,
        group_id=GetAccountGroupId(name='Equity').id)

    with pytest.raises(NameError):
        _ = Account.create(
            name='Equity', user=test_user, parent=None,
            group_id=GetAccountGroupId(name='Equity').id)


@pytest.mark.usefixtures('test_accounts')
def test_fullname_property(db_session):
    """Tests account's fullname property"""
    account = db_session.query(Account).filter_by(name='Rent').first()

    assert account.fullname == 'Expenses - Housing - Rent'


@pytest.mark.usefixtures('test_accounts')
def test_depth_property_in_1st_level(db_session):
    """Tests account's depth property"""
    account = db_session.query(Account).filter_by(name='Expenses').first()

    assert account.depth == 1


@pytest.mark.usefixtures('test_accounts')
def test_depth_property_in_3rd_level(db_session):
    """Tests account's depth property"""
    account = db_session.query(Account).filter_by(name='Rent').first()

    assert account.depth == 3


@pytest.mark.usefixtures('test_accounts')
def test_descendents_method_without_subaccounts(db_session):
    """Assures that the Account.descendents() returns 0 values when there are no descendents."""
    account = db_session.query(Account).filter_by(name='Rent').first()

    assert account._descendents.count() == 0


@pytest.mark.usefixtures('test_accounts')
def test_descendents_method(db_session):
    """Assures that the Account.descendents() returns the full
    list of descendents from the queried account."""
    account = db_session.query(Account).filter_by(name='Expenses').first()

    assert account._descendents.count() == 38


@pytest.mark.usefixtures('test_accounts')
def test_is_leaf_property_for_inner_node(db_session):
    """Tests 'is_leaf' property, which returns a boolean indicating
    whether the queried account is a leaf (ie, has no descendents)."""
    account = db_session.query(Account).filter_by(name='Expenses').first()

    assert not account.is_leaf


@pytest.mark.usefixtures('test_accounts')
def test_is_leaf_property_for_leaf_node(db_session):
    """Tests 'is_leaf' property, which returns a boolean indicating
    whether the queried account is a leaf (ie, has no descendents)."""
    account = db_session.query(Account).filter_by(name='Rent').first()

    assert account.is_leaf


@pytest.mark.usefixtures('test_accounts')
def test_credit_card_account(test_user):
    """Tests polymorphism of credit card class."""
    account_types = set([account.type for account in test_user.accounts])
    assert 'credit_card' in account_types
