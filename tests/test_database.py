import sqlite3

import pytest

from finerplan import create_app
from finerplan.database import db

from tests import DataBaseFile

_INSERT_EXPENSES_BEVERAGES = """
INSERT INTO expenses (cash_date, description, value) 
VALUES ('2020-03-14', 'beverages for Pi day', '200.0');"""
_INSERT_EXPENSES_DONATION = """
INSERT INTO expenses (cash_date, description, value) 
VALUES ('2001-01-15', 'Donation to Wikipedia Foundation', '10000.00');"""
_INSERT_EXPENSES_TOWEL = """
INSERT INTO expenses (cash_date, description, value) 
VALUES ('2020-05-25', 'A new towel', '15.99');"""
_SELECT_COUNT_EXPENSES = "SELECT count(*) FROM expenses;"


def test_database_connect_in_app_context(app):
    """Database connects using the app configuration."""
    con = db.connect()
    con.execute(_INSERT_EXPENSES_BEVERAGES)
    con.commit()

    con = sqlite3.connect(app.config['SQLITE_DATABASE'])
    assert con.execute(_SELECT_COUNT_EXPENSES).fetchone() == (1, )


def test_database_fails_outside_app_context():
    """Database does not connect outside app context."""
    with pytest.raises(RuntimeError, match='outside of application context'):
        _ = db.connect()


@pytest.mark.xfail(reason="Database binds only to last initialized app.")
def test_database_attach_app_context():
    """Database binds to the current app context.

    Checks that in a multi-app scenarion, the db global variable always
    use the current app context.
    """
    with DataBaseFile() as tmp_file1, DataBaseFile() as tmp_file2:
        assert tmp_file1 != tmp_file2

        app1 = create_app(environment='testing')
        app1.config['SQLITE_DATABASE'] = tmp_file1

        app2 = create_app(environment='testing')
        app2.config['SQLITE_DATABASE'] = tmp_file2

        with app1.app_context():
            con = db.connect()
            db.create_all()
            con.execute(_INSERT_EXPENSES_BEVERAGES)
            con.commit()

        # Nothing was saved yet into app2 database
        con = sqlite3.connect(app2.config['SQLITE_DATABASE'])
        with pytest.raises(sqlite3.OperationalError, match='no such table: expenses'):
            con.execute(_SELECT_COUNT_EXPENSES).fetchone()

        with app2.app_context():
            con = db.connect()
            db.create_all()
            con.execute(_INSERT_EXPENSES_DONATION)
            con.execute(_INSERT_EXPENSES_TOWEL)
            con.commit()

        con = sqlite3.connect(app2.config['SQLITE_DATABASE'])
        assert con.execute(_SELECT_COUNT_EXPENSES).fetchone() == (2,)

        con = sqlite3.connect(app1.config['SQLITE_DATABASE'])
        assert con.execute(_SELECT_COUNT_EXPENSES).fetchone() == (1,)


def test_database_persist_accross_requests():
    """Database persists data between different requests."""
    app = create_app(environment='testing')
    with DataBaseFile() as tmp_file:
        app.config['SQLITE_DATABASE'] = tmp_file

        with app.app_context():
            con = db.connect()
            db.create_all()
            con.execute(_INSERT_EXPENSES_BEVERAGES)
            con.commit()
            assert con.execute(_SELECT_COUNT_EXPENSES).fetchone() == (1, )

        with app.app_context():
            con = db.connect()
            con.execute(_INSERT_EXPENSES_TOWEL)
            assert con.execute(_SELECT_COUNT_EXPENSES).fetchone() == (2, )


def test_database_persist_accross_apps():
    """Database persists data between different apps."""
    with DataBaseFile() as tmp_file:
        app1 = create_app(environment='testing')
        app1.config['SQLITE_DATABASE'] = tmp_file
        with app1.app_context():
            con = db.connect()
            db.create_all()
            con.execute(_INSERT_EXPENSES_BEVERAGES)
            con.commit()
            assert con.execute(_SELECT_COUNT_EXPENSES).fetchone() == (1, )

        app2 = create_app(environment='testing')
        app2.config['SQLITE_DATABASE'] = tmp_file
        with app2.app_context():
            con = db.connect()
            con.execute(_INSERT_EXPENSES_TOWEL)
            assert con.execute(_SELECT_COUNT_EXPENSES).fetchone() == (2, )
