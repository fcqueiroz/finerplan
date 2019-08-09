from datetime import date

from flask_wtf import FlaskForm
from wtforms import DateField, DecimalField, IntegerField, RadioField, SelectField, \
    StringField, SubmitField, HiddenField, SelectMultipleField
from wtforms.validators import DataRequired

from finerplan.model import GetAccountGroupId
from .custom_validators import OptionalIfFieldDifferentThan

from config import form_groups, report_names


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
    parent_id = HiddenField('Parent Account Id')
    name = StringField('Account Name', validators=[DataRequired()])
    group_id = SelectField('Account Group', validators=[DataRequired()], choices=[], coerce=int)
    closing = IntegerField(
        'Closing Day of Credit Card Invoice',
        validators=[
            OptionalIfFieldDifferentThan(field='group_id', delayed=GetAccountGroupId(name='Credit Card')),
            DataRequired()])
    payment = IntegerField(
        'Payment Day of Credit Card Invoice',
        validators=[
            OptionalIfFieldDifferentThan(field='group_id', delayed=GetAccountGroupId(name='Credit Card')),
            DataRequired()])
    submit = SubmitField('Create')


class AddReportCardForm(FlaskForm):
    name = StringField("Report Title", validators=[DataRequired()])
    if len(form_groups) == 1:
        group = StringField(
            'Report Type', validators=[DataRequired()], default=form_groups[0],
            render_kw={'class': "form-control", 'disabled': True})
    else:
        group = SelectField(
            'Report Type', validators=[DataRequired()], render_kw={'class': "custom-select"},
            choices=[("", "---")] + [(s, s) for s in form_groups])

    information_names = SelectMultipleField(
        'Information Reports',
        validators=[OptionalIfFieldDifferentThan(field='group', value='Information'), DataRequired()],
        choices=[(s, s) for s in report_names['Information']])
    table_names = SelectField(
        'Table Reports',
        validators=[OptionalIfFieldDifferentThan(field='group', value='Table'), DataRequired()],
        choices=[("", "---")] + [(s, s) for s in report_names['Table']])
    graph_names = SelectField(
        'Graph Reports',
        validators=[OptionalIfFieldDifferentThan(field='group', value='Graph'), DataRequired()],
        choices=[("", "---")] + [(s, s) for s in report_names['Graph']])

    submit = SubmitField('Create')
