from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from finerplan import db, login


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    accounts = db.relationship('Account', backref='owner', lazy='dynamic')
    cards = db.relationship('Card', backref='owner', lazy='dynamic')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def create(cls, username, email, password) -> 'User':
        """
        Public method to create a new user.
        """
        password_hash = generate_password_hash(password)
        new_user = cls(username=username, email=email, password_hash=password_hash)
        db.session.add(new_user)
        db.session.commit()

        return new_user

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(_id):
    return User.query.get(int(_id))
