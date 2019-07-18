from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, login


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    accounts = db.relationship('Account', backref='owner', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def __init__(self, username, email):
        self.username = username
        self.email = email

        # Create fundamental accounts
        for account in fundamental_accounts().values():
            self.create_account(account)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def create_account(self, account):
        if not self.has_account(account):
            self.accounts.append(account)

    def owned_accounts(self):
        return Account.query.filter_by(user_id=self.id)

    def has_account(self, other_account):
        accounts = self.owned_accounts()
        return accounts.filter_by(name=other_account.name).count() == 1

    def get_categories(self, kind):
        """Returns a list of already created categories by the user for a certain kind of transaction"""

        return account_categories(kind)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


def account_categories(kind):
    # Temporarily uses a hard-coded list of categories (until the other functionalities are implemented
    hard_categories = {
        'expenses': [
            'Housing - Rent', 'Housing - Furniture', 'Housing - Maintenance', 'Housing - Utilities',
            'Electronic devices - Phone', 'Electronic devices - Computer',
            'Personal care - Cosmetics', 'Personal care - Hairdresser', 'Personal care - Hair removal',
            'Personal care - Clothing',
            'Education - Courses', 'Education - Supplies', 'Education - Books',
            'Business',
            'Leisure - General', 'Leisure - Hobbies', 'Leisure - Vacation',
            'Food - Groceries', 'Food - Restaurants',
            'Other - Uncategorized', 'Other - Gifts and donations',
            'Health - Pharmacy', 'Health - Special care', 'Health - Doctors', 'Health - Medicine',
            'Transportation - Auto', 'Transportation - Public', 'Transportation - Taxi', 'Transportation - Travel'
        ],
        'income': ['Scholarship', 'Paycheck', 'Subsidy', 'Other', 'Business']
    }
    return hard_categories[kind]


def fundamental_accounts():
    """Creates the 5 fundamental accounts according to basic accounting rules

    ref: https://www.gnucash.org/docs/v3/C/gnucash-guide/basics-accounting1.html
    """
    accounts = {
        'assets': Account(name='Assets'),
        'liabilities': Account(name='Liabilities'),
        'equity': Account(name='Equity'),
        'income': Account(name='Income'),
        'expenses': Account(name='Expenses')
    }
    return accounts


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # transaction = db.relationship('Transaction', backref='owner', lazy='dynamic')

    def __repr__(self):
        try:
            return f'<Account {self.owner.username}\'s {self.name}>'
        except AttributeError:
            return f'<Account Unclaimed {self.name}>'


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # account_id_origin = db.Column(db.Integer, db.ForeignKey('account.id'))
    # account_id_destination = db.Column(db.Integer, db.ForeignKey('account.id'))
    # pay_method_id = db.Column(db.Integer, db.ForeignKey('payment_method.id'))
    # category_id = db.Column(db.Integer, db.ForeignKey('transaction_category.id'))
    value = db.Column(db.Float)
    installments = db.Column(db.Integer)
    accrual_date = db.Column(db.DateTime)
    # cash_date = db.Column(db.DateTime)
    description = db.Column(db.Text)
    kind = db.Column(db.String(64))

    def __repr__(self):
        return f'<{self.description[:24] + (self.description[24:] and "..")}\t({self.value})>'


class Expenses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pay_method = db.Column(db.String(128))
    accrual_date = db.Column(db.DateTime)
    cash_date = db.Column(db.DateTime)
    description = db.Column(db.Text)
    category = db.Column(db.String(128))
    category_1 = db.Column(db.String(128))
    category_2 = db.Column(db.String(128))
    value = db.Column(db.Float)


class Earnings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    accrual_date = db.Column(db.DateTime)
    cash_date = db.Column(db.DateTime)
    description = db.Column(db.Text)
    category = db.Column(db.String(128))
    value = db.Column(db.Float)


class BrokerageTransfers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    accrual_date = db.Column(db.DateTime)
    cash_date = db.Column(db.DateTime)
    custodian = db.Column(db.String(128))
    origin = db.Column(db.String(128))
    description = db.Column(db.Text)
    value = db.Column(db.Float)


class Assets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(128))
    asset_class = db.Column(db.String(128))
    subclass = db.Column(db.String(128))
    asset = db.Column(db.String(128))
    maturity = db.Column(db.String(128))
    aim_bool = db.Column(db.Integer)
    aim = db.Column(db.Float)


class Investments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    code = db.Column(db.String(128))
    quantity = db.Column(db.Float)
    value = db.Column(db.Float)
    custodian = db.Column(db.String(128))
    notes = db.Column(db.Text)


class ValueHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(128))
    date = db.Column(db.String(128))
    quantity = db.Column(db.Float)
    unit_value = db.Column(db.Float)
    gross_value = db.Column(db.Float)
    net_value = db.Column(db.Float)


class Rendimentos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(128))
    asset = db.Column(db.String(128))
    carteira = db.Column(db.Float)
    aporte = db.Column(db.Float)
    cotas = db.Column(db.Float)
    valor_cotas = db.Column(db.Float)
    medium_annual_price = db.Column(db.Float)
    medium_historical_price = db.Column(db.Float)
    month_earning = db.Column(db.Float)
    year_earning = db.Column(db.Float)
    total_earning = db.Column(db.Float)
