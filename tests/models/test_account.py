
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
