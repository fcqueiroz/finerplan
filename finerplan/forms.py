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
	installments = IntegerField("Installments", default=1, validators=[DataRequired()])
	transaction = RadioField("Type of Transaction",
                             choices=[('earnings', form_words['earnings']),
                                      ('assets', form_words['assets']),
                                      ('expenses', form_words['expenses'])])
	pay_method = RadioField("Payment Method",
	                         choices=[(form_words['cash'], form_words['cash']),
	                                  (form_words['credit'], form_words['credit']),
	                                  (form_words['outsourced'], form_words['outsourced'])])
	category_0 = SelectField("Category", default="Mercado", choices = generate_categories()[0])
	#category_1 = SelectField("Category", choices = generate_categories()[1])
	#category_2 = StringField("Category")
#	pay_method = SelectField("Payment Method", choices = [(1, "Dinheiro"), (2, "Cartão de Crédito"), (3, "Terceiros")], validators=[DataRequired()], coerce=str)
#	category_0 = SelectField("Category", choices = generate_categories()[0], validators=[DataRequired()])
#	category_1 = SelectField("Category", choices = generate_categories()[1], validators=[DataRequired()])
#	category_2 = SelectField("Category", choices = generate_categories()[2], validators=[DataRequired()])
	submit = SubmitField("Add it")

class TestForm(AddTransactionForm):

	category_2 = SelectField("Category", choices = generate_categories()[2])
