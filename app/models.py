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

    def __init__(self, password=None, *args, **kwargs):
        # 'password' is an optional argument for now, but might become obligatory in future
        super().__init__(*args, **kwargs)
        if password is not None:
            self.set_password(password)

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
    # depth = db.Column(db.Integer)
    # is_leaf = db.Column(db.Boolean, default=True)
    # transaction = db.relationship('Transaction', backref='owner', lazy='dynamic')

    def __repr__(self):
        return f'<Account {self.id} {self.name}>'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # After the account creation, run 'generate_path'. Fix this!

        # self.depth = len(self._split_path())
        # self.is_leaf = True

    def generate_path(self, parent=None):
        if parent is not None:
            path = parent.path + '.'
        else:
            path = ''
        self.path = path + str(self.id)

    @property
    def fullname(self):
        path_nodes = self.path.split('.')
        path_names = [Account.query.get(int(node)).name for node in path_nodes]
        return ' - '.join(path_names)

    @staticmethod
    def _update_parent(parent_node):
        """Changes parent attributes to indicate it is not a leaf node anymore"""
        if isinstance(parent_node, Account):
            parent_node.is_leaf = False

    def get_descendents(self, root, min_depth=None, max_depth=None, inner=False):
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
        inner: bool, default=False
            By default returns only the leaf nodes. If True, returns inner nodes as well.
        """
        root_path = root.path + str(root.id) + self._path_sep_number + '%'
        base_depth = root.depth
        children = self.query.filter(Account.path.like(root_path))

        if min_depth is not None:
            children = children.filter(base_depth + min_depth <= Account.depth)

        if max_depth is not None:
            children = children.filter(Account.depth <= base_depth + max_depth)

        if not inner:
            children = children.filter(Account.is_leaf)

        return children

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
        """Returns a list of all the subaccounts under a hierarchy that are leaf nodes.

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
            if root is not None:
                children = root.get_descendents(root, inner=False).all()
                if root.is_leaf:
                    subaccounts.append(root)
                if children:
                    subaccounts.extend(children)

        return subaccounts


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
