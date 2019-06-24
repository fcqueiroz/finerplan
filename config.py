import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    NAME = os.getenv("LOGNAME").capitalize()
    CREDIT_CLOSING = 11  # Day of month when the credit card invoice closes
    CREDIT_PAYMENT = 25  # Day of month when the credit card invoice is paid
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    DATABASE = os.path.join(basedir, 'finerplan.db')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE  # or os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


# Defines common words used in the forms
form_words = {'earnings': "Receita",
              'expenses': "Gasto",
              'brokerage_transfers': "Investimento",
              'cash': "Dinheiro",
              'credit': "Crédito",
              'outsourced': "Terceiros"}
