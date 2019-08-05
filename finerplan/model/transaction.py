from sqlalchemy.sql import func

from finerplan import db


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

        deposits = transactions.filter(cls.destination_id == account.id)
        deposits_sum = deposits.with_entities(func.coalesce(func.sum(cls.value), 0)).first()[0]

        withdraws = transactions.filter(cls.source_id == account.id)
        withdraws_sum = withdraws.with_entities(func.coalesce(func.sum(cls.value), 0)).first()[0]

        return deposits_sum - withdraws_sum

    @classmethod
    def _accrual_date_filter(cls, start, end):
        filters = []
        if start is not None:
            filters.append((start <= cls.accrual_date))
        if end is not None:
            filters.append((cls.accrual_date <= end))

        return filters
