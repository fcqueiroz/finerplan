from flask import Flask
import os
import sqlite3

app = Flask(__name__) # create the application instance
app.config.from_object(__name__) # load config from this file

# Load default config and override config from an environment variable
app.config.update(dict(
    NAME=os.getenv("LOGNAME").capitalize(),
    DATABASE=os.path.join(app.root_path, 'finerplan.db'),
    CREDIT_CLOSING=11,  # Day of month when the credit card invoice closes
    CREDIT_PAYMENT=25,  # Day of month when the credit card invoice is paid
    SECRET_KEY=(os.environ.get('SECRET_KEY') or "you-will-never-guess"),
))

# Defines common words used in the forms
form_words = {'earnings': "Receita",
              'expenses': "Gasto",
              'brokerage_transfers': "Investimento",
              'cash': "Dinheiro",
              'credit': "Crédito",
              'outsourced': "Terceiros"}

# Creates the tables if they don't exist.
con = sqlite3.connect(app.config['DATABASE'],  check_same_thread=False)
with app.open_resource('schema.sql', mode='r') as f:
    con.cursor().executescript(f.read())
con.commit()
con.close()

from finerplan import routes
