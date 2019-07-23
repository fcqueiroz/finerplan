from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, login
from config import fundamental_accounts


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    accounts = db.relationship('Account', backref='owner', lazy='dynamic')

    def __init__(self, password=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 'password' is an optional argument for now, but might become obligatory in future
        if password is not None:
            self.set_password(password)

    def init_accounts(self):
        """Init fundamental user accounts."""
        for account_name in fundamental_accounts:
            new_account = Account(user_id=self.id, name=account_name)
            db.session.add(new_account)
            db.session.commit()

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(_id):
    return User.query.get(int(_id))


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    path = db.Column(db.String(500), index=True)

    # transaction = db.relationship('Transaction', backref='owner', lazy='dynamic')

    def __repr__(self):
        return f'<Account {self.id} {self.name}>'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # After the account creation, run 'generate_path'. Fix this!

    def generate_path(self, parent=None):
        if parent is not None:
            path = parent.path + '.'
        else:
            path = ''
        self.path = path + str(self.id)

    @property
    def fullname(self):
        """
        Returns the name of all the accounts parents accounts in a single string.
        """
        path_nodes = self.path.split('.')
        path_names = [Account.query.get(int(node)).name for node in path_nodes]

        return ' - '.join(path_names)

    @property
    def depth(self):
        """
        Returns how deep a certain account is in the hierarchy
        """
        return len(self.path.split('.'))

    def descendents(self):
        """
        Returns the descendents from self.
        """
        children_path = self.path + '.%'
        children = self.query.filter(Account.path.like(children_path))

        return children.all()

    @property
    def is_leaf(self):
        """Returns a boolean indicating whether the queried account
        is a leaf (ie, has no descendents)."""
        return len(self.descendents()) == 0


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_source = db.Column(db.Integer, db.ForeignKey('account.id'))
    account_destination = db.Column(db.Integer, db.ForeignKey('account.id'))
    # pay_method_id = db.Column(db.Integer, db.ForeignKey('payment_method.id'))
    value = db.Column(db.Float)
    installments = db.Column(db.Integer)
    accrual_date = db.Column(db.DateTime)
    # cash_date = db.Column(db.DateTime)
    description = db.Column(db.Text)
    kind = db.Column(db.String(64))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f'<{self.description[:24] + (self.description[24:] and "..")}\t({self.value})>'
