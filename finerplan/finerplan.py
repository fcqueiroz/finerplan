import os
from flask import Flask

app = Flask(__name__) # create the application instance
app.config.from_object(__name__) # load config from this file

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE = os.path.join(app.root_path, 'finerplan.db'),
    SECRET_KEY = (os.environ.get('SECRET_KEY') or 'you-will-never-guess'),
))

import finerplan.routes
