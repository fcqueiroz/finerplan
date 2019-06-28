# Standard Library
from datetime import datetime
import os
import unittest
from warnings import warn
# 3rd Party Libraries
from flask import url_for
import sqlite3
# Local Imports
from app import create_app, db, reports
from app.models import User, Transaction, Account
from app.sql import SqliteOps
from config import date_model

_test_basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sql = SqliteOps()
correct_config = {
    'testing': {'TESTING': True, 'DEBUG': True,
                'DATABASE': os.path.join(_test_basedir, 'test_fp.db')},
    'development': {'TESTING': False, 'DEBUG': True,
                    'DATABASE': os.path.join(_test_basedir, 'dev_fp.db')},
    'production': {'TESTING': False, 'DEBUG': False,
                   'DATABASE': os.path.join(_test_basedir, 'finerplan.db')}
}
basic_accounts = ['Generic income sources', 'Generic expenses']


def _check_is_testing_database(database):
    """Returns true if the database engine is pointing to the testing database"""
    testing_sqlalchemy_database_uri = 'sqlite:///' + os.path.join(_test_basedir, 'test_fp.db')
    context_uri = str(database.engine.url)

    return testing_sqlalchemy_database_uri == context_uri


class TestRouting(unittest.TestCase):

    urls = ['/', '/overview', '/expenses']
    pages = ['simple_page.' + p for p in ['overview', 'expenses']]

    @classmethod
    def setUpClass(cls):
        _app = create_app('testing')
        cls.app = _app

    def test_get_url(self):
        """Check the 'GET' response is correct based on url route"""
        for url in self.urls:
            with self.subTest(url=url):
                with self.app.app_context():
                    response = self.app.test_client().get(url)
                self.assertEqual(200, response.status_code, msg=f"wrong status code for '{url}'")
                self.assertIn('text/html', response.content_type, msg=f"wrong content type for '{url}'")

    def test_get_view(self):
        """Check the 'GET' response is correct based on view name using url_for"""
        for page in self.pages:
            with self.subTest(page=page):
                with self.app.app_context():
                    response = self.app.test_client().get(url_for(page))

                self.assertEqual(200, response.status_code, msg=f"wrong status code for '{page}' page")
                self.assertIn('text/html', response.content_type, msg=f"wrong content type for '{page}' page")


class TestSQL(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        con = sqlite3.connect(correct_config['development']['DATABASE'], check_same_thread=False)
        cur = con.cursor()
        cls.table_category_len = cls.read_from_db(cur)
        con.close()

    @staticmethod
    def read_from_db(cur):
        table_category_len = {}
        for table in ['expenses', 'earnings']:
            query = f'SELECT category FROM {table} GROUP BY category;'
            cur.execute(query)
            r = cur.fetchall()
            table_category_len[table] = len(r)
        return table_category_len

    def test_last_expenses(self):
        r = sql.last_expenses(num=10)

        self.assertIsInstance(r, list)
        self.assertLessEqual(len(r), 10)
        if len(r) > 0:
            self.assertEqual(len(r[0]), 5)
        else:
            warn(f"Nothing was returned in '{self.test_last_expenses.__name__}' query")

    def test_last_earnings(self):
        r = sql.last_earnings()

        self.assertIsInstance(r, list)
        if len(r) > 0:
            self.assertEqual(len(r[0]), 5)
        else:
            warn(f"Nothing was returned in '{self.test_last_earnings.__name__}' query")

    def test_last_investments(self):
        r = sql.last_investments()

        self.assertIsInstance(r, list)
        if len(r) > 0:
            self.assertEqual(len(r[0]), 4)
        else:
            warn(f"Nothing was returned in '{self.test_last_investments.__name__}' query")

    def test_generate_categories(self):
        for table in ['expenses', 'earnings']:
            with self.subTest(table=table):
                r = sql.generate_categories(table)
                self.assertIsInstance(r, list)
                self.assertEqual(len(r), self.table_category_len[table])

                if self.table_category_len[table] > 0:
                    row = r[0]

                    self.assertIsInstance(row, tuple)
                    self.assertEqual(len(row), 2)
                    self.assertEqual(row[0], row[1])
                else:
                    self.assertEqual(r, [('Category 1', 'Category 1'),
                                         ('Category 2', 'Category 2'),
                                         ('Category 3', 'Category 3')])


class TestReports(unittest.TestCase):
    def test_basic(self):
        basic_report = reports.basic()
        self.assertIsInstance(basic_report, dict)
        self.assertEqual(len(basic_report.keys()), 15)


class TestAppCreation(unittest.TestCase):
    def test_environment_creation(self):
        """For each environment check whether the app loaded the correct configuration"""
        for app_env in correct_config.keys():
            with self.subTest(app_env=app_env):
                _app = create_app(config_name=app_env)
                for cfg in ['TESTING', 'DEBUG']:
                    self.assertEqual(_app.config[cfg], correct_config[app_env][cfg])

    def test_database_engines(self):
        """Check we are connected to the right database in each environment"""
        for app_env in correct_config.keys():
            with self.subTest(app_env=app_env):
                _app = create_app(config_name=app_env)
                with _app.app_context():
                    sqlalchemy_database_uri = 'sqlite:///' + correct_config[app_env]['DATABASE']
                    self.assertEqual(str(db.engine.url), sqlalchemy_database_uri)


class TestDatabaseOperation(unittest.TestCase):
    ctx = None

    @classmethod
    def setUpClass(cls):
        _app = create_app('testing')
        cls.ctx = _app.app_context()
        cls.ctx.push()
        db.create_all()

        # Create table sample data
        cls.users = cls.create_users()
        cls.accounts = cls.create_accounts(cls.users)
        cls.transactions = cls.create_transactions()

    @classmethod
    def tearDown(cls):
        db.session.rollback()

    @classmethod
    def tearDownClass(cls):
        if _check_is_testing_database(db):
            db.session.remove()
            db.drop_all()
        cls.ctx.pop()

    @staticmethod
    def create_users():
        u = [User(username="john", email="john@example.com"),
             User(username='susan', email='susan@example.com')]
        return u

    @staticmethod
    def create_accounts(users):
        """Create some accounts"""
        acc = [Account(name='Wallet', owner=users[0]),
               Account(name='Checking account', owner=users[0]),
               Account(name='Saving account', owner=users[1])]
        return acc

    @staticmethod
    def create_transactions():
        dt = datetime.strptime('2019-06-25', date_model)
        t = [Transaction(value=4.20, accrual_date=dt, description="Bus ticket"),
             Transaction(value=81.35, accrual_date=dt,
                         description="I'm a really long but really useful transaction description")]
        return t

    def test_user_table(self):
        self.assertTrue(_check_is_testing_database(db), msg="NOT using test database")

        # Include accounts in database
        for u in self.users:
            db.session.add(u)
        db.session.commit()

        users = User.query.all()

        self.assertEqual(str(users), '[<User john>, <User susan>]', msg="Wrong users representation")

    def test_account_ownership(self):
        self.assertTrue(_check_is_testing_database(db), msg="NOT using test database")

        # Include accounts in database
        for acc in self.accounts:
            db.session.add(acc)
        db.session.commit()

        # Check accounts owned by the user1
        u = User.query.get(1)
        accounts = str(u.accounts.all())
        self.assertIn('<Account Wallet>', accounts)
        self.assertIn('<Account Checking account>', accounts)
        self.assertNotIn('<Account Saving account>', accounts)

        # Check accounts owned by the user2
        u = User.query.get(2)
        accounts = str(u.accounts.all())
        self.assertNotIn('<Account Wallet>', accounts)
        self.assertNotIn('<Account Checking account>', accounts)
        self.assertIn('<Account Saving account>', accounts)

    @unittest.skip("Basic account binding not implemented yet")
    def test_user_basic_account(self):
        """Ensure that whenever a user is created, some basic accounts are created together"""
        # Create a user
        user = self.users[0]
        db.session.add(user)

        accs = Account.query.all()
        for a in accs:
            print(a.id, a.owner.username, a.name)

        # Check these accounts are correctly listed
        u = User.query.get(1)
        accounts = str(u.accounts.all())
        for acc in basic_accounts:
            self.assertIn(acc, accounts)

    def test_transaction_table(self):
        self.assertTrue(_check_is_testing_database(db), msg="NOT using test database")

        # Include transactions in database
        for t in self.transactions:
            db.session.add(t)

        # Check representation
        # Descriptions smaller than 24 characters should be printed as they are
        short_transaction = Transaction.query.get(1)
        _description = str(short_transaction)
        self.assertEqual(_description, "<Bus ticket\t(4.2)>")
        # Descriptions longer than 24 characters should be truncated
        long_transaction = Transaction.query.get(2)
        _description = str(long_transaction)
        self.assertEqual(_description, "<I'm a really long but re..\t(81.35)>")


if __name__ == '__main__':
    unittest.main()
