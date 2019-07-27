from flask_login import UserMixin
from sqlalchemy.sql import func
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, login

from config import fundamental_accounts


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    accounts = db.relationship('Account', backref='owner', lazy='dynamic')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def create(cls, username, email, password) -> 'User':
        """
        Public method to create a new user.
        """
        new_user = cls(username=username, email=email)
        new_user.set_password(password=password)
        db.session.add(new_user)
        db.session.commit()

        return new_user

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(_id):
    return User.query.get(int(_id))


def init_fundamental_accounts(user):
    # Initialize user accounts here
    for account_name in fundamental_accounts:
        try:
            Account.create(name=account_name, user=user)
        except NameError:
            pass  # Account is already created


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    path = db.Column(db.String(500), index=True)
    group = db.Column(db.String(64))
    # TODO: Transform properties into hybrid properties so SQLAlchemy can query them

    def __repr__(self):
        return f'<Account {self.id} {self.name}>'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def create(cls, name, user, parent=None) -> 'Account':
        """
        Public method to create an account linked to an user.

        Parameters
        ----------
        name: str
            Name of the new account.
        user: models.User
            User object to which the new account will be linked to.
        parent: models.Account
            If passed, the new account will become a subaccount of
            parent Account and will have the same type.
        """
        if cls.check_unique_fullname(name=name, user=user, parent=parent):
            new_account = cls(name=name, user_id=user.id)
            db.session.add(new_account)
            db.session.commit()

        else:
            raise NameError("Each account's fullname must be unique.")

        new_account._generate_path(parent=parent)
        db.session.commit()

        new_account._define_group(parent=parent)
        db.session.commit()

        return new_account

    @classmethod
    def check_unique_fullname(cls, name, user, parent):
        if parent is not None:
            base_fullname = parent.fullname + ' - '
        else:
            base_fullname = ''

        account = cls.query.filter(
            cls.name == name,
            cls.user_id == user.id).all()

        if not account:
            return True

        for _account in account:
            if _account.fullname == base_fullname + name:
                return False

        return True

    def _generate_path(self, parent=None) -> None:
        if parent is not None:
            path = parent.path + '.'
        else:
            path = ''
        self.path = path + str(self.id)

    def _define_group(self, parent=None) -> None:
        if parent is not None:
            group = parent.group
        else:
            group = self.name.lower()
        self.group = group

    @property
    def fullname(self):
        """
        Returns the name of all the account's parents accounts in a single string.
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
        """
        Returns a boolean indicating whether the queried account
        is a leaf (ie, has no descendents).
        """
        return len(self.descendents()) == 0

    def balance(self, start=None, end=None) -> float:
        """
        Evaluates the difference between account's deposits and
        withdraws during a provided period time.

        Paramenters
        -----------
        start: date like object
            The beginning of the evaluation period.
        end: date like object
            The ending of the evaluation period.
        """
        filters = self._accrual_date_filter(start, end)

        deposits_sum = self._balance(self.deposits, filters)
        withdraws_sum = self._balance(self.withdraws, filters)

        return deposits_sum - withdraws_sum

    @staticmethod
    def _balance(query, filters):
        result = query.filter(*filters).with_entities(func.sum(Transaction.value)).first()[0]
        if result is None:
            return 0
        else:
            return result

    @staticmethod
    def _accrual_date_filter(start, end):
        filters = []
        if start is not None:
            filters.append((start <= Transaction.accrual_date))
        if end is not None:
            filters.append((Transaction.accrual_date <= end))

        return filters


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(db.Integer, db.ForeignKey('account.id'))
    source = db.relationship(
        'Account',
        foreign_keys=[source_id],
        backref=db.backref('withdraws', lazy='dynamic'))
    destination_id = db.Column(db.Integer, db.ForeignKey('account.id'))
    destination = db.relationship(
        'Account',
        foreign_keys=[destination_id],
        backref=db.backref('deposits', lazy='dynamic'))
    # pay_method_id = db.Column(db.Integer, db.ForeignKey('payment_method.id'))
    value = db.Column(db.Float)
    installments = db.Column(db.Integer)
    accrual_date = db.Column(db.DateTime)
    # cash_date = db.Column(db.DateTime)
    description = db.Column(db.Text)
    # kind = db.Column(db.String(64))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f'<{self.description[:24] + (self.description[24:] and "..")}\t({self.value})>'
