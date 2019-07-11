from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    accounts = db.relationship('Account', backref='owner', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # transaction = db.relationship('Transaction', backref='owner', lazy='dynamic')

    def __repr__(self):
        return f'<Account {self.owner.username}\'s {self.name}>'


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # account_id_origin = db.Column(db.Integer, db.ForeignKey('account.id'))
    # account_id_destination = db.Column(db.Integer, db.ForeignKey('account.id'))
    # pay_method_id = db.Column(db.Integer, db.ForeignKey('payment_method.id'))
    # category_id = db.Column(db.Integer, db.ForeignKey('transaction_category.id'))
    value = db.Column(db.Float)
    installments = db.Column(db.Integer)
    accrual_date = db.Column(db.DateTime)
    cash_date = db.Column(db.DateTime)
    description = db.Column(db.Text)

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
