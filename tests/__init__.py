from finerplan import db
from finerplan.model.account_groups import init_account_groups

__all__ = ["setup_db", "clean_db", "teardown_db"]


def setup_db(app):
    """Method used to build a database"""
    db.app = app
    db.create_all()


def seed_db():
    """Method used to insert into database data needed for minimal use."""
    init_account_groups()


def teardown_db():
    """Method used to destroy a database"""
    db.session.remove()
    db.drop_all()
    db.session.bind.dispose()


def clean_db():
    """Clean all data, leaving schema as is

    Suitable to be run before each db-aware test. This is much faster than
    dropping whole schema an recreating from scratch.
    """
    for table in reversed(db.metadata.sorted_tables):
        db.session.execute(table.delete())
