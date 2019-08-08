from finerplan import db


class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))


card_report = db.Table(
    'card_report',
    db.Column('card_id', db.Integer, db.ForeignKey('card.id'), primary_key=True),
    db.Column('report_id', db.Integer, db.ForeignKey('report.id'), primary_key=True)
)


class Card(db.Model):
    __tablename__ = 'card'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(50))
    genre = db.Column(db.String(50))

    reports = db.relationship('Report', secondary=card_report, lazy='dynamic')

    @classmethod
    def create(cls, user, name, genre, **kwargs) -> 'Card':
        """
        Public method to create a Card linked to an user.

        Parameters
        ----------
        user: finerplan.model.user.User
            User object to which the new Card will be linked to.
        name: str
            Name of the new Card
        genre: str
            Name of the Card's report group
        """
        new_card = cls(user_id=user.id, name=name, genre=genre)
        db.session.add(new_card)
        db.session.flush()

        card_report_names = cls._select_kwargs(genre, **kwargs)
        card_reports = Report.query.filter(Report.name.in_(card_report_names))
        new_card.reports.extend(card_reports)

        db.session.commit()

        return new_card

    @staticmethod
    def _select_kwargs(genre, **kwargs):
        if genre == 'Information':
            return kwargs.get('information_kinds')
        else:
            raise ValueError(f"Unknown genre='{genre}'")
