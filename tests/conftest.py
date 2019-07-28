# 3rd Party Libraries
import pytest
# Local Imports
from finerplan import create_app, db as _db
from finerplan.models import User, Account, Transaction

from tests import setup_db, teardown_db, clean_db
from tests.data import users, accounts, transactions


@pytest.fixture(scope="session")
def app():
    """Global application fixture

    Initialized with testing config file.
    """
    _app = create_app(config_name='testing')
    ctx = _app.app_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.fixture(scope="session")
def db(app):
    """Creates clean database schema and drops it on teardown

    Note, that this is a session scoped fixture, it will be executed only once
    and shared among all tests. Use `db_session` fixture to get clean database
    before each test.
    """

    setup_db(app)
    yield _db
    teardown_db()


@pytest.fixture(scope="function")
def db_session(db, app):
    """Provides clean database before each test. After each test,
    session.rollback() is issued.

    Return sqlalchemy session.
    """

    with app.app_context():
        clean_db()
        yield db.session
        db.session.rollback()


@pytest.fixture(scope='function')
def client(app):
    return app.test_client()


@pytest.fixture(scope="function")
def test_user(db_session):
    """
    Creates a single test user
    """
    user_data = users.alice()
    user = User.create(**user_data)

    return user


@pytest.fixture(scope="function")
def test_accounts(db_session, test_user):
    """
    Creates some accounts for test user
    """
    expenses = Account.create(name=accounts.expenses()['name'], user=test_user)
    earnings = Account.create(name=accounts.earnings()['name'], user=test_user)
    equity = Account.create(name=accounts.equity()['name'], user=test_user)
    housing = Account.create(name=accounts.housing()['name'], user=test_user, parent=expenses)
    rent = Account.create(name=accounts.rent()['name'], user=test_user, parent=housing)

    _all_accounts = [expenses, earnings, equity, housing, rent]
    return _all_accounts


@pytest.fixture(scope='function')
def test_transaction(db_session, test_accounts):
    """
    Creates a single transaction
    """
    source = test_accounts[1]  # Earnings account
    destination = test_accounts[0]  # Expenses account

    transaction = transactions.first_salary()
    transaction.source_id = source.id
    transaction.destination_id = destination.id

    db_session.add(transaction)
    db_session.commit()
    return transaction


@pytest.fixture(scope='function')
def test_transactions(db_session, test_accounts):
    """
    Creates some transactions
    """
    def insert(_transaction, source, destination):
        _transaction.source_id = source.id
        _transaction.destination_id = destination.id
        db_session.add(_transaction)
        db_session.commit()
        return _transaction

    # From Earnings to Equity
    first_salary = insert(transactions.first_salary(), test_accounts[1], test_accounts[2])
    # From Equity to Expenses
    dining_out = insert(transactions.dining_out(), test_accounts[2], test_accounts[0])
    # From Equity to Expenses
    phone_bill = insert(transactions.phone_bill(), test_accounts[2], test_accounts[0])

    _all_transactions = [first_salary, dining_out, phone_bill]
    return _all_transactions
