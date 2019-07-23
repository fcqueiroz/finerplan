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
def test_accounts(db_session):
    """
    Creates some accounts for test user
    """
    _test_user = test_user()
    _all_accounts = accounts.all_accounts
    for account in _all_accounts:
        account.user_id = _test_user.id
        db_session.add(account)
    db_session.commit()
    return _all_accounts


@pytest.fixture(scope='function')
def test_transaction(db_session):
    """
    Creates a single transaction
    """
    source = accounts.earnings()
    destination = accounts.expenses()

    transaction = transactions.first_salary()
    transaction.account_source = source.id
    transaction.account_destination = destination.id

    db_session.add(transaction)
    db_session.commit()
    return transaction
