from finerplan import db
from sqlalchemy.orm.exc import NoResultFound

from .account import Account, CreditCard
from .accounting_group import AccountingGroup
from .card import Card
from .report import Report
from .transaction import Transaction
from .user import User

from config import accounting_types, report_names


def init_accounting_group():
    """
    Inserts into AccountingGroup the data needed for aplication.
    """
    for group in accounting_types.keys():
        for name in accounting_types[group]:
            try:
                _ = AccountingGroup.query.filter_by(name=name, group=group).one()
            except NoResultFound:
                db.session.add(AccountingGroup(name=name, group=group))
    db.session.commit()


def init_report():
    """
    Inserts into Report the data needed for aplication.
    """
    for group in report_names.keys():
        for name in report_names[group]:
            try:
                _ = Report.query.filter_by(name=name, group=group).one()
            except NoResultFound:
                db.session.add(Report(name=name, group=group))
    db.session.commit()
