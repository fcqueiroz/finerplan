from finerplan import db

card_report = db.Table(
    'card_report',
    db.Column('card_id', db.Integer, db.ForeignKey('card.id'), primary_key=True),
    db.Column('report_id', db.Integer, db.ForeignKey('report.id'), primary_key=True)
)


class Card(db.Model):
    __tablename__ = 'card'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(64), nullable=False)

    reports = db.relationship('Report', secondary=card_report, lazy='dynamic')

    @classmethod
    def create(cls, user, name) -> 'Card':
        """
        Public method to create a Card linked to an user.

        Parameters
        ----------
        user: finerplan.model.user.User
            User object to which the new Card will be linked to.
        name: str
            Name of the new Card
        """
        new_card = cls(user_id=user.id, name=name)
        db.session.add(new_card)
        db.session.commit()

        return new_card
