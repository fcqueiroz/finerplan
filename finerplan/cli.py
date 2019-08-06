from finerplan.model.account_groups import init_account_groups


def register(app):
    @app.cli.command()
    def seed():
        """Load initial data into database."""
        print("Seeding database...")

        with app.app_context():
            init_account_groups()
