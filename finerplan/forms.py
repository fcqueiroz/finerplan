from datetime import date

from flask_wtf import FlaskForm
from wtforms import BooleanField, DateField, IntegerField, PasswordField, RadioField, SelectField, \
    StringField, SubmitField
from wtforms.validators import DataRequired

from config import form_words
from finerplan.sql import generate_categories


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


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
    cat_expense = SelectField("Category", default="Mercado", choices=generate_categories('expenses'))
    cat_earning = SelectField("Category", default="Mercado", choices=generate_categories('earnings'))

    submit = SubmitField("Add it")
