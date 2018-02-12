from datetime import date

from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, SelectField, IntegerField
from wtforms import RadioField, DateField
from wtforms.validators import DataRequired

from .finerplan import form_words
from finerplan.sql import generate_categories

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
	cat_expense = SelectField("Category", default="Mercado", choices = generate_categories('expenses'))
	cat_earning = SelectField("Category", default="Mercado", choices = generate_categories('earnings'))

	submit = SubmitField("Add it")

#class AddExpenseForm(AddTransactionForm):


#class AddEarningForm(AddTransactionForm):
#	cat_expense = SelectField("Category", default="Mercado", choices = generate_categories()[0])

#class AddInvestmentForm(AddTransactionForm):

class TestForm(AddTransactionForm):

	category_2 = SelectField("Category", choices = generate_categories()[2])
