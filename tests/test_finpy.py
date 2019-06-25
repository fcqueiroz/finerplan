# Standard Library
import unittest
# Local Imports
from finerplan import app, reports, sql


class TestHome(unittest.TestCase):
    def test_get(self):
        response = app.test_client().get('/')
        self.assertEqual(200, response.status_code)


class TestSQL(unittest.TestCase):
    def test_last_expenses(self):
        r = sql.last_expenses(num=10)

        assert isinstance(r, list)
        assert len(r) <= 10
        if len(r) > 0:
            assert len(r[0]) == 5

    def test_last_earnings(self):
        r = sql.last_earnings()

        assert isinstance(r, list)
        if len(r) > 0:
            assert len(r[0]) == 5

    def test_last_investments(self):
        r = sql.last_investments()

        assert isinstance(r, list)
        if len(r) > 0:
            assert len(r[0]) == 4


class TestReports(unittest.TestCase):
    def test_basic(self):
        basic_report = reports.basic()
        assert isinstance(basic_report, dict)
        assert len(basic_report.keys()) == 15


if __name__ == '__main__':
    unittest.main()
