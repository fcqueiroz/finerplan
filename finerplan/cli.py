from finerplan import db
from finerplan.model.account import AccountGroups


def register(app):
    @app.cli.command()
    def seed():
        """Load initial data into database."""
        print("Seeding database...")
        account_groups_list = ['Equity', 'Income', 'Expense', 'Cash']

        with app.app_context():
            for group_name in account_groups_list:
                result = AccountGroups.query.filter_by(name=group_name).first()
                if result is None:
                    db.session.add(AccountGroups(name=group_name))
            db.session.commit()
