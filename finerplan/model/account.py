from sqlalchemy.ext.hybrid import hybrid_property

from finerplan import db


class Account(db.Model):
    __tablename__ = 'account'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    path = db.Column(db.String(500), index=True)
    group_id = db.Column(db.Integer, db.ForeignKey('account_groups.id'))
    _group = db.relationship("AccountGroups")
    type = db.Column(db.String(50))
    # TODO: Transform properties into hybrid properties so SQLAlchemy can query them

    def __repr__(self):
        return f'<Account {self.id} {self.name}>'

    @classmethod
    def create(cls, name, user, group_id, parent=None, **kwargs) -> 'Account':
        """
        Public method to create an account linked to an user.

        Parameters
        ----------
        name: str
            Name of the new account.
        user: models.User
            User object to which the new account will be linked to.
        group_id: int
            Group'id this account belongs
        parent: models.Account
            If passed, the new account will become a subaccount of
            parent Account and will have the same type.
        """
        if cls.check_unique_fullname(name=name, user=user, parent=parent):
            new_account = cls(name=name, user_id=user.id, group_id=group_id, **kwargs)
            db.session.add(new_account)
            db.session.commit()

        else:
            raise NameError("Each account's fullname must be unique.")

        new_account._generate_path(parent=parent)

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
        children = Account.query.filter(Account.path.like(children_path))

        return children.all()

    @property
    def is_leaf(self):
        """
        Returns a boolean indicating whether the queried account
        is a leaf (ie, has no descendents).
        """
        return len(self.descendents()) == 0

    @hybrid_property
    def group(self):
        return self._group.name

    __mapper_args__ = {
        "polymorphic_identity": "account",
        "polymorphic_on": type,
    }


class CreditCard(Account):
    __tablename__ = 'credit_card'
    id = db.Column(db.Integer, db.ForeignKey('account.id'), primary_key=True)
    closing = db.Column(db.Integer)
    payment = db.Column(db.Integer)

    @classmethod
    def create(cls, closing, payment, **kwargs) -> 'Account':
        new_account = super().create(closing=closing, payment=payment, **kwargs)
        return new_account

    __mapper_args__ = {
        "polymorphic_identity": "credit_card",
    }
