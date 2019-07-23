
import pytest

from app.models import Account


@pytest.mark.usefixtures('test_accounts')
def test_account_path_attribute(db_session):
    """Checks that the path attribute is correctly assigned"""
    hierarchy = ['Expenses', 'Housing', 'Rent']
    _accounts = [db_session.query(Account).filter_by(name=name).first() for name in hierarchy]
    expected_path = '.'.join([str(account.id) for account in _accounts])

    assert _accounts[-1].path == expected_path


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
