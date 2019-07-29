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
