from finerplan.model import init_accounting_group, init_report


def register(app):
    @app.cli.command()
    def seed():
        """Load initial data into database."""
        print("Seeding database...")

        with app.app_context():
            init_accounting_group()
            init_report()
