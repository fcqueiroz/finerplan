from datetime import date

from flask_wtf import FlaskForm
from wtforms import DateField, DecimalField, IntegerField, RadioField, SelectField, \
    StringField, SubmitField, HiddenField, SelectMultipleField
from wtforms.validators import DataRequired

from finerplan.model import AccountGroups
from .custom_validators import OptionalIfFieldDifferentThan

from config import genres, report_names


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


class GetGroupId(object):
    """
    Returns the id of an account group based on the given name.
    """
    def __init__(self, name):
        self.name = name

    def __call__(self):
        group = AccountGroups.query.filter_by(name=self.name).one_or_none()
        try:
            return group.id
        except AttributeError:
            return None


class AddAccountForm(FlaskForm):
    parent_id = HiddenField('Parent Account Id')
    name = StringField('Account Name', validators=[DataRequired()])
    group_id = SelectField('Account Group', validators=[DataRequired()], choices=[], coerce=int)
    closing = IntegerField(
        'Closing Day of Credit Card Invoice',
        validators=[OptionalIfFieldDifferentThan(field='group_id', delayed=GetGroupId(name='Credit Card')), DataRequired()])
    payment = IntegerField(
        'Payment Day of Credit Card Invoice',
        validators=[OptionalIfFieldDifferentThan(field='group_id', delayed=GetGroupId(name='Credit Card')), DataRequired()])
    submit = SubmitField('Create')


class AddReportForm(FlaskForm):
    name = StringField("Report Title", validators=[DataRequired()])
    if len(genres) == 1:
        genre = StringField(
            'Report Type', validators=[DataRequired()], default=genres[0],
            render_kw={'class': "form-control", 'disabled': True})
    else:
        genre = SelectField(
            'Report Type', validators=[DataRequired()], render_kw={'class': "custom-select"},
            choices=[("", "---")] + [(s, s) for s in genres])

    information_names = SelectMultipleField(
        'Information Reports',
        validators=[OptionalIfFieldDifferentThan(field='genre', value='Information'), DataRequired()],
        choices=[(s, s) for s in report_names['Information']])
    table_names = SelectField(
        'Table Reports',
        validators=[OptionalIfFieldDifferentThan(field='genre', value='Table'), DataRequired()],
        choices=[("", "---")] + [(s, s) for s in report_names['Table']])
    graph_names = SelectField(
        'Graph Reports',
        validators=[OptionalIfFieldDifferentThan(field='genre', value='Graph'), DataRequired()],
        choices=[("", "---")] + [(s, s) for s in report_names['Graph']])

    submit = SubmitField('Create')
