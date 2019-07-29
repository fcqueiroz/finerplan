from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from finerplan import db, login


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    accounts = db.relationship('Account', backref='owner', lazy='dynamic')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def create(cls, username, email, password) -> 'User':
        """
        Public method to create a new user.
        """
        new_user = cls(username=username, email=email)
        new_user.set_password(password=password)
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
