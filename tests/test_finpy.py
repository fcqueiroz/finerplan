# Standard Library
import os
import unittest
# 3rd Party Libraries
import sqlite3
# Local Imports
from finerplan import app, create_app, db, reports, sql

_test_basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
correct_config = {
    'testing': {'TESTING': True, 'DEBUG': True,
                'DATABASE': os.path.join(_test_basedir, 'test_fp.db')},
    'development': {'TESTING': False, 'DEBUG': True,
                    'DATABASE': os.path.join(_test_basedir, 'dev_fp.db')},
    'production': {'TESTING': False, 'DEBUG': False,
                   'DATABASE': os.path.join(_test_basedir, 'finerplan.db')}
}


class TestHome(unittest.TestCase):

    pages = ['/', '/overview', '/expenses']

    def test_get(self):
        for page in self.pages:
            with self.subTest(page=page):
                response = app.test_client().get(page)
                self.assertEqual(200, response.status_code)

    def test_content_type(self):
        for page in self.pages:
            with self.subTest(page=page):
                response = app.test_client().get(page)
                self.assertIn('text/html', response.content_type)


class TestSQL(unittest.TestCase):

    con = None

    @classmethod
    def setUpClass(cls):
        cls.con = sqlite3.connect(correct_config['development']['DATABASE'], check_same_thread=False)

        cls.read_from_db(cls.con.cursor())

    @classmethod
    def read_from_db(cls, cur):
        cls.table_category_len = {}
        for table in ['expenses', 'earnings']:
            query = f'SELECT category FROM {table} GROUP BY category;'
            cur.execute(query)
            r = cur.fetchall()
            cls.table_category_len[table] = len(r)

    @classmethod
    def tearDownClass(cls):
        cls.con.close()

    def test_last_expenses(self):
        r = sql.last_expenses(num=10)

        self.assertIsInstance(r, list)
        self.assertLessEqual(len(r), 10)
        if len(r) > 0:
            self.assertEqual(len(r[0]), 5)

    def test_last_earnings(self):
        r = sql.last_earnings()

        self.assertIsInstance(r, list)
        if len(r) > 0:
            self.assertEqual(len(r[0]), 5)

    def test_last_investments(self):
        r = sql.last_investments()

        self.assertIsInstance(r, list)
        if len(r) > 0:
            self.assertEqual(len(r[0]), 4)

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


if __name__ == '__main__':
    unittest.main()
