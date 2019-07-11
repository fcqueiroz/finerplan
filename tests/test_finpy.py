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
from config import date_model, app_config

_test_basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sql = SqliteOps()
basic_accounts = ['Generic income sources', 'Generic expenses']


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
                assert 200 == response.status_code, f"wrong status code for '{url}'"
                assert 'text/html' in response.content_type, f"wrong content type for '{url}'"

    def test_get_view(self):
        """Check the 'GET' response is correct based on view name using url_for"""
        for page in self.pages:
            with self.subTest(page=page):
                with self.app.app_context():
                    response = self.app.test_client().get(url_for(page))

                assert 200 == response.status_code, f"wrong status code for '{page}' page"
                assert 'text/html' in response.content_type, f"wrong content type for '{page}' page"


class TestSQL(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        con = sqlite3.connect(app_config(config_name='development').DATABASE, check_same_thread=False)
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
            assert len(r[0]) == 5
        else:
            warn(f"Nothing was returned in '{self.test_last_expenses.__name__}' query")

    def test_last_earnings(self):
        r = sql.last_earnings()

        self.assertIsInstance(r, list)
        if len(r) > 0:
            assert len(r[0]) == 5
        else:
            warn(f"Nothing was returned in '{self.test_last_earnings.__name__}' query")

    def test_last_investments(self):
        r = sql.last_investments()

        self.assertIsInstance(r, list)
        if len(r) > 0:
            assert len(r[0]) == 4
        else:
            warn(f"Nothing was returned in '{self.test_last_investments.__name__}' query")

    def test_generate_categories(self):
        for table in ['expenses', 'earnings']:
            with self.subTest(table=table):
                r = sql.generate_categories(table)
                self.assertIsInstance(r, list)
                assert len(r) == self.table_category_len[table]

                if self.table_category_len[table] > 0:
                    row = r[0]

                    self.assertIsInstance(row, tuple)
                    assert len(row) == 2
                    assert row[0] == row[1]
                else:
                    assert r == [('Category 1', 'Category 1'),
                                 ('Category 2', 'Category 2'),
                                 ('Category 3', 'Category 3')]


class TestReports(unittest.TestCase):
    def test_basic(self):
        basic_report = reports.basic()
        self.assertIsInstance(basic_report, dict)
        assert len(basic_report.keys()) == 15


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
        # Include accounts in database
        for u in self.users:
            db.session.add(u)
        db.session.commit()

        users = User.query.all()

        assert str(users) == '[<User john>, <User susan>]', "Wrong users representation"

    @unittest.skip("This method is being refatored")
    def test_account_ownership(self):
        # Include accounts in database
        for acc in self.accounts:
            db.session.add(acc)
        db.session.commit()

        # Check accounts owned by the user1
        u = User.query.get(1)
        accounts = str(u.accounts.all())
        assert '<Account Wallet>' in accounts
        assert '<Account Checking account>' in accounts
        assert '<Account Saving account>' not in accounts

        # Check accounts owned by the user2
        u = User.query.get(2)
        accounts = str(u.accounts.all())
        assert '<Account Wallet>' not in accounts
        assert '<Account Checking account>' not in accounts
        assert '<Account Saving account>' in accounts

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
            assert acc in accounts

    def test_transaction_table(self):
        # Include transactions in database
        for t in self.transactions:
            db.session.add(t)

        # Check representation
        # Descriptions smaller than 24 characters should be printed as they are
        short_transaction = Transaction.query.get(1)
        _description = str(short_transaction)
        assert _description == "<Bus ticket\t(4.2)>"
        # Descriptions longer than 24 characters should be truncated
        long_transaction = Transaction.query.get(2)
        _description = str(long_transaction)
        assert _description == "<I'm a really long but re..\t(81.35)>"


if __name__ == '__main__':
    unittest.main()
