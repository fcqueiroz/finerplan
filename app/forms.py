from datetime import date

from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import BooleanField, DateField, DecimalField, IntegerField, PasswordField, RadioField, SelectField, \
    StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError

from app.models import User, Account


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


class UniqueFullname(object):
    """
    Checks if the provided new account name has an unique fullname.

    :param parent_id:
        The name of the field containing the id of the parent account.
    :param message:
        Error message to raise in case of a validation error.
    """
    def __init__(self, parent_id, message=None):
        self.parent_id = parent_id
        if not message:
            message = u"There is an account using this name under the same parent account"
        self.message = message

    def __call__(self, form, field):
        parent_id = form[self.parent_id]
        parent = Account.query.get(parent_id.data)
        if not Account.check_unique_fullname(field.data, current_user, parent):
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


class AddTransactionForm(FlaskForm):
    description = StringField("Description", validators=[DataRequired()])
    accrual_date = DateField("Registry Date", default=date.today(), validators=[DataRequired()])
    value = DecimalField("Value", validators=[DataRequired()])
    transaction_kind = RadioField(
        "Type of Transaction", validators=[DataRequired()],
        choices=[(kind.lower(), kind) for kind in ['Income', 'Expenses']])
    installments = IntegerField("Installments", default=1, validators=[DataRequired()])
    source_id = SelectField('Source Account', validators=[DataRequired()], choices=[], coerce=int)
    destination_id = SelectField('Destination Account', validators=[DataRequired()], choices=[], coerce=int)
    submit = SubmitField("Add it")


class AddAccountForm(FlaskForm):
    parent_id = IntegerField('Parent Account Id', validators=[DataRequired()])
    name = StringField('Account Name', validators=[DataRequired(), UniqueFullname('parent_id')])
    submit = SubmitField('Create')
