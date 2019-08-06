from datetime import datetime
import pytest

from finerplan.model import Account, AccountGroups, CreditCard

from tests.data import accounts


def test_create_account(test_user):
    """Tests method to create an account linked to a user."""
    account_data = accounts.equity()
    return_value = Account.create(
        name=account_data['name'], user=test_user, parent=None,
        group_id=AccountGroups.query.filter_by(name='Equity').first().id)

    assert test_user.accounts.count() == 1
    assert test_user.accounts.first() == return_value
    assert return_value.name == account_data['name']
    assert return_value.path == '1'
    assert return_value.group == account_data['group']


def test_create_account_refuses_duplicated_fullname(test_user):
    """
    Tests that method to create an account linked to a user does
    not allow the creation of two accounts with the same fullname.
    """
    _ = Account.create(
        name='Equity', user=test_user, parent=None,
        group_id=AccountGroups.query.filter_by(name='Equity').first().id)

    with pytest.raises(NameError):
        _ = Account.create(
            name='Equity', user=test_user, parent=None,
            group_id=AccountGroups.query.filter_by(name='Equity').first().id)


def test_create_account_subaccount(test_user):
    """Tests method to create a subaccount."""
    parent_account = Account.create(
        name=accounts.expenses()['name'], user=test_user,
        group_id=AccountGroups.query.filter_by(name='Expenses').first().id)

    account = Account.create(
        name=accounts.housing()['name'], user=test_user, parent=parent_account,
        group_id=AccountGroups.query.filter_by(name='Expenses').first().id)

    assert test_user.accounts.count() == 2
    assert account.path == '1.2'


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

    assert len(account.descendents()) == 0


@pytest.mark.usefixtures('test_accounts')
def test_descendents_method(db_session):
    """Assures that the Account.descendents() returns the full
    list of descendents from the queried account."""
    account = db_session.query(Account).filter_by(name='Expenses').first()

    assert len(account.descendents()) == 2


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


@pytest.mark.usefixtures('test_transaction')
def test_account_deposits(db_session):
    """Tests relationship betwen Account and Transaction between the deposits attribute."""
    source = db_session.query(Account).filter_by(name='Income').first()
    destination = db_session.query(Account).filter_by(name='Expenses').first()

    assert source.deposits.count() == 0
    assert destination.deposits.count() == 1


@pytest.mark.usefixtures('test_transaction')
def test_account_withdraws(db_session):
    """Tests relationship betwen Account and Transaction between the withdraws attribute."""
    source = db_session.query(Account).filter_by(name='Income').first()
    destination = db_session.query(Account).filter_by(name='Expenses').first()

    assert source.withdraws.count() == 1
    assert destination.withdraws.count() == 0


@pytest.mark.usefixtures('test_accounts')
def test_credit_card_account(test_user):
    """Tests polymorphism of credit card class."""

    existing_accounts = test_user.accounts.count()
    account_data = accounts.turn_group_into_id(accounts.card_3412())
    _ = CreditCard.create(user=test_user, **account_data)

    assert test_user.accounts.count() == existing_accounts + 1
