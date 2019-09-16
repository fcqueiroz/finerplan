import os
basedir = os.path.abspath(os.path.dirname(__file__))


class UserInfo(object):
    """Regular information about the default user"""
    NAME = os.getenv("LOGNAME", "Username").capitalize()
    CREDIT_CLOSING = 11  # Day of month when the credit card invoice closes
    CREDIT_PAYMENT = 25  # Day of month when the credit card invoice is paid


class BaseConfig(object):
    """Parent configuration class."""
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(BaseConfig):
    """Configurations for Development."""
    DEBUG = True
    DATABASE = os.path.join(basedir, 'dev.db')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE


class TestingConfig(BaseConfig):
    """Configurations for Testing, with a separate test database."""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    WTF_CSRF_ENABLED = False
    SERVER_NAME = 'localhost.localdomain'


class ProductionConfig(BaseConfig):
    """Configurations for Production."""
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DATABASE = os.path.join(basedir, 'old.db')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + DATABASE


def app_config(config_name=None):
    config_list = {
        'development': DevelopmentConfig,
        'testing': TestingConfig,
        'production': ProductionConfig,
    }

    if config_name is None:
        config_name = os.getenv('FLASK_ENV')

    return config_list[config_name]


# Defines prefered date model in database
date_model = '%Y-%m-%d'


# Defines common words used in the forms
form_words = {'earnings': "Receita",
              'expenses': "Gasto",
              'brokerage_transfers': "Investimento",
              'cash': "Dinheiro",
              'credit': "Crédito",
              'outsourced': "Terceiros"}


# Model
# ref: https://www.gnucash.org/docs/v3/C/gnucash-guide/basics-accounting1.html
accounting_types = {
    'Asset': ['Cash', 'Bank', 'Stock', 'Mutual Fund', 'Accounts Receivable', 'Asset'],
    'Equity': ['Equity'],
    'Expense': ['Expense'],
    'Income': ['Income'],
    'Liability': ['Credit Card', 'Accounts Payable', 'Liability']
}

# Reports
form_available_report_groups = ['Information', 'Table']  # Planned to include 'Graph' soon
