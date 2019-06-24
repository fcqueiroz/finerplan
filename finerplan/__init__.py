from flask import Flask
import sqlite3

from config import Config

app = Flask(__name__)  # create the application instance
app.config.from_object(Config)  # load config from this file

# Creates the tables if they don't exist.
con = sqlite3.connect(app.config['DATABASE'],  check_same_thread=False)
with app.open_resource('schema.sql', mode='r') as f:
    con.cursor().executescript(f.read())
con.commit()
con.close()

from finerplan import routes
