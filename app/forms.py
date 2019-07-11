from datetime import date

from flask_wtf import FlaskForm
from wtforms import BooleanField, DateField, IntegerField, PasswordField, RadioField, SelectField, \
    StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError

from app.sql import SqliteOps
from app.models import User
from config import form_words

sql = SqliteOps()


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username).first()
        if user is not None:
            raise ValidationError('This username is already being used.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email).first()
        if user is not None:
            raise ValidationError('This email is already being used.')


class AddTransactionForm(FlaskForm):
    description = StringField("Description", validators=[DataRequired()])
    date = DateField("Registry Date", default=date.today(), validators=[DataRequired()])
    value = StringField("Value", validators=[DataRequired()])
    transaction = RadioField("Type of Transaction",
                             choices=[('earnings', form_words['earnings']),
                                      ('brokerage_transfers', form_words['brokerage_transfers']),
                                      ('expenses', form_words['expenses'])])

    pay_method = RadioField("Payment Method",
                            choices=[(form_words['cash'], form_words['cash']),
                                     (form_words['credit'], form_words['credit']),
                                     (form_words['outsourced'], form_words['outsourced'])])
    installments = IntegerField("Installments", default=1, validators=[DataRequired()])
    new_cat = StringField("New Category")
    cat_expense = SelectField("Category", default="Mercado", choices=sql.generate_categories('expenses'))
    cat_earning = SelectField("Category", default="Mercado", choices=sql.generate_categories('earnings'))

    submit = SubmitField("Add it")
