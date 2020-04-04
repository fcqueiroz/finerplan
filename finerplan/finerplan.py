import os
from flask import Flask
import sqlite3

from config import obtain_config_object

app = Flask(__name__) # create the application instance

app.config.from_object(obtain_config_object(environment=app.config['ENV']))
app.config.update(dict(
    NAME=os.getenv("LOGNAME").capitalize(),
    CREDIT_CLOSING=11,  # Day of month when the credit card invoice closes
    CREDIT_PAYMENT=25,  # Day of month when the credit card invoice is paid
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

import finerplan.routes
