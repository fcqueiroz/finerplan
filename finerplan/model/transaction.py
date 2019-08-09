from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func

from finerplan import db


class Installment(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'), nullable=False)
    cash_date = db.Column(db.Date, nullable=False)
    value = db.Column(db.Numeric(precision=14, scale=4), nullable=False)


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    source_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    destination_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    accrual_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=False)
    # pay_method_id = db.Column(db.Integer, db.ForeignKey('payment_method.id'))
    # kind = db.Column(db.String(64))

    source = db.relationship(
        'Account',
        foreign_keys=[source_id],
        backref=db.backref('withdraws', lazy='dynamic'))
    destination = db.relationship(
        'Account',
        foreign_keys=[destination_id],
        backref=db.backref('deposits', lazy='dynamic'))
    installments = db.relationship('Installment', lazy='dynamic')

    def __repr__(self):
        return f'<{self.description[:24] + (self.description[24:] and "..")}\t({self.value})>'

    @classmethod
    def create(cls, description, accrual_date, source_id, destination_id, value, installments=1) -> 'Transaction':
        """
        Public method to create a transaction and its linked installments.

        Parameters
        ----------
        description: str
            Transaction description
        accrual_date: datetime
            Date when transaction happened
        source_id: int
            Account'id which was the source of the transfered value amount.
        destination_id: int
            Account'id which was the destination of the transfered value amount.
        value: float
            Total transaction's value
        installments: int
            Number of installments
        Returns
        -------
        finerplan.model.transaction.Transaction
        """
        transaction = cls(
            source_id=source_id, destination_id=destination_id,
            description=description, accrual_date=accrual_date)
        db.session.add(transaction)
        db.session.flush()
        source = transaction.source

        new_data = source.list_installments(transaction=transaction, value=value, installments=installments)
        new_installments = [Installment(transaction_id=transaction.id, **_data) for _data in new_data]
        db.session.add_all(new_installments)

        db.session.commit()

        return transaction

    @classmethod
    def balance(cls, account, start=None, end=None) -> float:
        """
        Evaluates the difference between deposits and withdraws
        for a specific account during a provided period time.

        Paramenters
        -----------
        start: date like object
            The beginning of the evaluation period.
        end: date like object
            The ending of the evaluation period.
        """

        filters = cls._accrual_date_filter(start, end)
        transactions = cls.query.filter(*filters)

        deposits = transactions.filter(cls.destination_id == account.id).join(cls.installments)
        deposits_sum = deposits.with_entities(func.coalesce(func.sum(Installment.value), 0)).first()[0]

        withdraws = transactions.filter(cls.source_id == account.id).join(cls.installments)
        withdraws_sum = withdraws.with_entities(func.coalesce(func.sum(Installment.value), 0)).first()[0]

        return deposits_sum - withdraws_sum

    @hybrid_property
    def value(self):
        return self.installments.with_entities(func.coalesce(func.sum(Installment.value), 0)).first()[0]

    @value.expression
    def value(cls):
        return cls.query.join(cls.installments).with_entities(func.coalesce(func.sum(Installment.value), 0)).first()[0]

    @classmethod
    def _accrual_date_filter(cls, start, end):
        filters = []
        if start is not None:
            filters.append((start <= cls.accrual_date))
        if end is not None:
            filters.append((cls.accrual_date <= end))

        return filters
