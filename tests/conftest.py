# 3rd Party Libraries
import pytest
# Local Imports
from app import create_app, db as _db

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
    user = users.alice()
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture(scope="function")
def test_accounts(db_session, test_user):
    """
    Creates some accounts for test user
    """
    _test_user = test_user

    def insert(_account, parent=None):
        _account.user_id = _test_user.id
        db_session.add(_account)
        db_session.commit()
        _account.generate_path(parent=parent)
        return _account

    expenses = insert(accounts.expenses())
    earnings = insert(accounts.earnings())
    equity = insert(accounts.equity())
    housing = insert(accounts.housing(), parent=expenses)
    rent = insert(accounts.rent(), parent=housing)

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
