# 3rd Party Libraries
import pytest
# Local Imports
from finerplan import create_app, db as _db
from finerplan.model import User, Account, CreditCard, Transaction, Card, Report, add_common_accounts, GetAccountGroupId

from tests import setup_db, teardown_db, clean_db, seed_db
from data.tests import accounts, users, transactions, card_report


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
def test_accounts(db_session, test_user) -> None:
    """
    Creates some accounts for test user
    """
    add_common_accounts(test_user)

    credit_card = accounts.visa()
    credit_card['group_id'] = credit_card['group'].id
    del credit_card['group']

    CreditCard.create(user=test_user, **credit_card)


@pytest.fixture(scope='function')
def test_transactions(db_session, test_accounts) -> None:
    """
    Creates some transactions
    """
    cash = Account.query.filter_by(name='Cash').one()

    Transaction.create(
        source_id=Account.query.filter_by(name='Paycheck').one().id,
        destination_id=cash.id, **transactions.first_salary())
    Transaction.create(
        source_id=cash.id, **transactions.dining_out(),
        destination_id=Account.query.filter_by(name='Restaurants').one().id)
    Transaction.create(
        source_id=cash.id, **transactions.phone_bill(),
        destination_id=Account.query.filter_by(name='Utilities').one().id)


@pytest.fixture(scope='function')
def test_card(db_session, test_transactions, test_user):
    """
    Creates a single report Card
    """
    form_data = card_report.test_report()
    card = Card.create(user=test_user, name=form_data.pop('name'))
    Report.assign_to(card, **form_data)

    return card
