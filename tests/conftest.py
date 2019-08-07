# 3rd Party Libraries
import pytest
# Local Imports
from finerplan import create_app, db as _db
from finerplan.model import User, Account, CreditCard, Transaction

from tests import setup_db, teardown_db, clean_db, seed_db
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
        seed_db()
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

    new_account = accounts.turn_group_into_id(accounts.expenses())
    expenses = Account.create(user=test_user, **new_account)

    new_account = accounts.turn_group_into_id(accounts.income())
    income = Account.create(user=test_user, **new_account)

    new_account = accounts.turn_group_into_id(accounts.equity())
    equity = Account.create(user=test_user, **new_account)

    new_account = accounts.turn_group_into_id(accounts.housing())
    housing = Account.create(user=test_user, parent=expenses, **new_account)

    new_account = accounts.turn_group_into_id(accounts.rent())
    rent = Account.create(user=test_user, parent=housing, **new_account)

    new_account = accounts.turn_group_into_id(accounts.card_3412())
    credit_card = CreditCard.create(user=test_user, **new_account)

    new_account = accounts.turn_group_into_id(accounts.devices())
    devices = Account.create(user=test_user, **new_account)

    _all_accounts = [expenses, income, equity, housing, rent, credit_card, devices]
    return _all_accounts


@pytest.fixture(scope='function')
def test_transactions(db_session, test_accounts):
    """
    Creates some transactions
    """
    expenses, income, equity = test_accounts[0:3]

    first_salary = Transaction.create(source_id=income.id, destination_id=equity.id, **transactions.first_salary())
    dining_out = Transaction.create(source_id=equity.id, destination_id=expenses.id, **transactions.dining_out())
    phone_bill = Transaction.create(source_id=equity.id, destination_id=expenses.id, **transactions.phone_bill())

    _all_transactions = [first_salary, dining_out, phone_bill]
    return _all_transactions
