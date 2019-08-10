from sqlalchemy.ext.hybrid import hybrid_property

from finerplan import db


class Account(db.Model):
    __tablename__ = 'account'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(64), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    path = db.Column(db.String(500), nullable=False)  # This should be unique..
    group_id = db.Column(db.Integer, db.ForeignKey('accounting_group.id'), nullable=False)
    # TODO: Find a way to eliminate the type column and use the group's name as the polymorphic identity
    type = db.Column(db.String(64), nullable=False)

    _group = db.relationship("AccountingGroup")

    # TODO: Create a Closure Table hierarchy.
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
        user: finerplan.model.user.User
            User object to which the new account will be linked to.
        group_id: int
            Group'id this account belongs
        parent: models.Account
            If passed, the new account will become a subaccount of
            parent Account and will have the same type.
        """
        if cls.check_unique_fullname(name=name, user=user, parent=parent):
            if parent is not None:
                base_path = parent.path + '.'
            else:
                base_path = ''

            new_account = cls(name=name, user_id=user.id, path=base_path, group_id=group_id, **kwargs)
            db.session.add(new_account)

            db.session.flush()
            path = new_account.path + str(new_account.id)
            assert path != base_path
            new_account.path = path

            db.session.commit()
        else:
            raise NameError("Each account's fullname must be unique.")

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

    @hybrid_property
    def _descendents(self):
        """
        Returns the descendents from self.
        """
        children_path = self.path + '.%'
        return Account.query.filter(Account.path.like(children_path))

    @hybrid_property
    def is_leaf(self):
        """
        Returns a boolean indicating whether the queried account
        is a leaf (ie, has no descendents).
        """
        return self._descendents.count() == 0

    @is_leaf.expression
    def is_leaf(cls):
        raise NotImplementedError

    def list_installments(self, **kwargs) -> list:
        return self._group.installments_enumerator(account=self, **kwargs)

    __mapper_args__ = {
        "polymorphic_identity": "account",
        "polymorphic_on": type,
    }


class CreditCard(Account):
    __tablename__ = 'credit_card'
    id = db.Column(db.Integer, db.ForeignKey('account.id'), primary_key=True, nullable=False)
    closing = db.Column(db.Integer, nullable=False)
    payment = db.Column(db.Integer, nullable=False)

    @classmethod
    def create(cls, closing, payment, **kwargs) -> 'Account':
        return super().create(closing=closing, payment=payment, **kwargs)

    def list_installments(self, **kwargs) -> list:
        return super().list_installments(closing_day=self.closing, payment_day=self.payment, **kwargs)

    __mapper_args__ = {
        "polymorphic_identity": "credit_card",
    }
