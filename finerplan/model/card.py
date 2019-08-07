from finerplan import db


class CardReports(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.Integer, db.ForeignKey('card.id'))
    kind = db.Column(db.String(50))


class Card(db.Model):
    __tablename__ = 'card'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(50))

    reports = db.relationship('CardReports', lazy='dynamic')

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
        new_card = cls(user_id=user.id, name=name)
        db.session.add(new_card)
        db.session.flush()

        kinds = cls._select_kwargs(genre, **kwargs)
        reports = [CardReports(card_id=new_card.id, kind=k) for k in kinds]
        db.session.add_all(reports)

        db.session.commit()

        return new_card

    @staticmethod
    def _select_kwargs(genre, **kwargs):
        if genre == 'information':
            return kwargs.get('information_kinds')
        else:
            raise ValueError(f"Unknown genre='{genre}'")
