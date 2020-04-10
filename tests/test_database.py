import sqlite3

import pytest

from finerplan import create_app
from finerplan.database import db

from tests import DataBaseFile


def test_database_connect_in_app_context(app):
    """Database connects using the app configuration."""
    db.execute("INSERT INTO expenses (cash_date, description, value) "
               "VALUES ('2020-03-14', 'beverages for Pi day', '200.0');")
    db.commit()

    con = sqlite3.connect(app.config['SQLITE_DATABASE'])
    assert con.execute("SELECT count(*) FROM expenses;").fetchone() == (1, )


def test_database_fails_outside_app_context():
    """Database does not connect outside app context."""
    with pytest.raises(RuntimeError, match='outside of application context'):
        db.connect()


def test_database_persist_accross_requests():
    """Database persists data between different requests."""
    app = create_app(environment='testing')
    with DataBaseFile() as tmp_file:
        app.config['SQLITE_DATABASE'] = tmp_file

        with app.app_context():
            db.create_all()
            db.execute("INSERT INTO expenses (cash_date, description, value) "
                       "VALUES ('2020-03-14', 'beverages for Pi day', '200.0');")
            db.commit()
            assert db.execute("SELECT count(*) FROM expenses;").fetchone() == (1, )

        with app.app_context():
            db.execute("INSERT INTO expenses (cash_date, description, value) "
                       "VALUES ('2020-05-25', 'A new towel', '15.99');")
            assert db.execute("SELECT count(*) FROM expenses;").fetchone() == (2, )


def test_database_persist_accross_apps():
    """Database persists data between different apps."""
    with DataBaseFile() as tmp_file:
        app1 = create_app(environment='testing')
        app1.config['SQLITE_DATABASE'] = tmp_file
        with app1.app_context():
            db.create_all()
            db.execute("INSERT INTO expenses (cash_date, description, value) "
                       "VALUES ('2020-03-14', 'beverages for Pi day', '200.0');")
            db.commit()
            assert db.execute("SELECT count(*) FROM expenses;").fetchone() == (1, )

        app2 = create_app(environment='testing')
        app2.config['SQLITE_DATABASE'] = tmp_file
        with app2.app_context():
            db.execute("INSERT INTO expenses (cash_date, description, value) "
                       "VALUES ('2020-05-25', 'A new towel', '15.99');")
            assert db.execute("SELECT count(*) FROM expenses;").fetchone() == (2, )
