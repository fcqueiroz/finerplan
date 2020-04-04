import os
from flask import Flask

from config import obtain_config_object

app = Flask(__name__) # create the application instance

app.config.from_object(obtain_config_object(environment=app.config['ENV']))
app.config.update(dict(
    NAME=os.getenv("LOGNAME", 'anon').capitalize(),
))

from finerplan.sql import create_tables

create_tables(database=app.config['DATABASE'])

import finerplan.routes
