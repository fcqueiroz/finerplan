from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, DecimalField
from wtforms.validators import DataRequired
from finpy.sql import generate_categories
    
class AddTransactionForm(FlaskForm):
	description = StringField('Description', validators=[DataRequired()])
	date = StringField('Registry Date', validators=[DataRequired()])
	value = StringField('Value', validators=[DataRequired()])
	pay_method = StringField('Payment Method')
	category_0 = StringField('Category', validators=[DataRequired()])
	category_1 = StringField('Category')
	category_2 = StringField('Category')
#	pay_method = SelectField('Payment Method', choices = [(1, 'Dinheiro'), (2, 'Cartão de Crédito'), (3, 'Terceiros')], validators=[DataRequired()], coerce=str)
#	category_0 = SelectField('Category', choices = generate_categories()[0], validators=[DataRequired()])
#	category_1 = SelectField('Category', choices = generate_categories()[1], validators=[DataRequired()])
#	category_2 = SelectField('Category', choices = generate_categories()[2], validators=[DataRequired()])
	submit = SubmitField('Add it')
