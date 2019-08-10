from finerplan import db
from finerplan.model import Account, CreditCard, AccountingGroup, Card, Report, Transaction, User
from finerplan.model import init_accounting_group, init_report
from finerplan.reports import InformationReport, TableReport

from config import accounting_types


def register(app):
    @app.cli.command()
    def seed():
        """Load initial data into database."""
        print("Seeding database...")

        with app.app_context():
            init_accounting_group(accounting_types)
            available_reports = dict(
                Information=InformationReport.available_reports(),
                Table=TableReport.available_reports())
            init_report(available_reports)

    @app.shell_context_processor
    def inject_models():
        return {
            'db': db, 'User': User,
            'Account': Account, 'CreditCard': CreditCard,
            'AccountingGroup': AccountingGroup,
            'Card': Card, 'Report': Report,
            'Transaction': Transaction}
