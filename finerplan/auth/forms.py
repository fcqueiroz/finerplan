from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError

from finerplan.models import User


class CorrectPassword(object):
    """
    Checks if the password is correct when the username is valid.

    :param username:
        The name of the username field.
    :param message:
        Error message to raise in case of a validation error.
    """
    def __init__(self, username, message=None):
        self.username = username
        if not message:
            message = u'Invalid password'
        self.message = message

    def __call__(self, form, field):
        username = form[self.username]
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            if not user.check_password(field.data):
                raise ValidationError(self.message)


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), CorrectPassword('username')])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is None:
            raise ValidationError('Invalid username')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=str(username)).first()
        if user is not None:
            raise ValidationError('This username is already being used.')

    def validate_email(self, email):
        user = User.query.filter_by(email=str(email)).first()
        if user is not None:
            raise ValidationError('This email is already being used.')
