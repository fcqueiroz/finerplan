from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, login
from config import default_account_categories, fundamental_accounts


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    accounts = db.relationship('Account', backref='owner', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def init_accounts(self):
        self._init_fundamental_accounts()
        self._init_default_account_categories()

    def _init_fundamental_accounts(self):
        # Create fundamental accounts
        for account_name in fundamental_accounts:
            self.create_account(account_name=account_name)

    def _init_default_account_categories(self):
        # Create default account categories
        for parent_account_name, account_list in default_account_categories:
            for account in account_list:
                self.create_account(account_name=account, parent_account_name=parent_account_name)

    def _add_account(self, account):
        if not isinstance(account, Account):
            raise ValueError(
                f"Can't create account with type '{type(account)}'. "
                f"Only Account object is allowed.")

        if not Account.query.filter_by(user_id=self.id, name=account.name) == 1:
            self.accounts.append(account)
            db.session.commit()

    def create_account(self, account_name, parent_account_name=None):
        """Create a new account within the accounts hierarchy

        Parameters
        ----------
        account_name: str
            Name of the new account
        parent_account_name: str, default None
            Name of the parent account in hierarchy
        """
        if parent_account_name is not None:
            parent_account = Account.query.filter_by(user_id=self.id, name=parent_account_name).first()
        else:
            parent_account = None

        new_account = Account(user_id=self.id, name=account_name, parent_account=parent_account)
        self._add_account(new_account)

    def get_subaccounts(self, root_names):
        """Returns a list of all the subaccounts under a hierarchy including the root account itself.

        Parameters
        ----------
        root_names: str, list-like
            The names of the accounts that represent the root of the tree hierarchy
        """
        if isinstance(root_names, str):
            root_names = [root_names]

        subaccounts = []
        for name in root_names:
            root = self.accounts.filter_by(name=name).first()
            children = root.get_descendents(root).all()
            subaccounts.append(root)
            if children:
                subaccounts.extend(children)

        return subaccounts

@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    path = db.Column(db.String(500), nullable=False, index=True)
    depth = db.Column(db.Integer)
    # transaction = db.relationship('Transaction', backref='owner', lazy='dynamic')

    def __repr__(self):
        try:
            return f'<Account {self.owner.username}\'s {self.name}>'
        except AttributeError:
            return f'<Account Unclaimed {self.name}>'

    def __init__(self, parent_account=None, **kwargs):
        super().__init__(**kwargs)
        self.path = self._generate_node_path(parent_account)
        self.depth = self._calculate_depth()

    @staticmethod
    def _generate_node_path(parent_node):
        if parent_node is None:
            path = '/'
        elif isinstance(parent_node, Account):
            path = ''.join([parent_node.path, str(parent_node.id), '/'])
        else:
            raise ValueError(f"Parent account must be Account type. Got '{type(parent_node)}'")

        return path

    def get_descendents(self, root, min_depth=None, max_depth=None):
        """Returns the descendents from a certain node.

        Parameters
        ----------
        root: Account instance
            The root node of the subtree returned
        min_depth: int, default=None
            The min difference of depth between the parent node depth and the children nodes.
            If min_depth is None, then the results starts on imediate children.
        max_depth: int, default=None
            The max difference of depth between the parent node depth and the children nodes.
            If max_depth is None, then the results are unbounded.
        """
        root_path = root.path + str(root.id) + '/%'
        base_depth = root.depth
        children = self.query.filter(Account.path.like(root_path))

        if min_depth is not None:
            children = children.filter(base_depth + min_depth <= Account.depth)

        if max_depth is not None:
            children = children.filter(Account.depth <= base_depth + max_depth)

        return children

    def _calculate_depth(self):
        nodes = list(filter(None, self.path.split('/')))
        return len(nodes)


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
