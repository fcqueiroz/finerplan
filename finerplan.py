from app import create_app, db
from app.models import User, Account, Transaction

app = create_app(config_name='development')


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Account': Account, 'Transaction': Transaction}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
