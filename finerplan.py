from finerplan import create_app, db
from finerplan.models import User, Account, Transaction

app = create_app(config_name='development')


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Account': Account, 'Transaction': Transaction}


if __name__ == '__main__':
    app.run(port=5001)
