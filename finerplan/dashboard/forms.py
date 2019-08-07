from datetime import date

from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import DateField, DecimalField, IntegerField, RadioField, SelectField, \
    StringField, SubmitField, HiddenField, SelectMultipleField
from wtforms.validators import DataRequired, ValidationError

from finerplan.model import Account, AccountGroups

from config import genres, information_report_kinds


class UniqueFullname(object):
    """
    Checks if the provided new account name has an unique fullname.

    :param other_field:
        The name of the field containing the parent account.
    :param message:
        Error message to raise in case of a validation error.
    """
    def __init__(self, other_field, message=None):
        self.other_field = other_field
        if not message:
            message = u"There is an account using this name under the same parent account."
        self.message = message

    def __call__(self, form, field):
        parent = form[self.other_field]
        if not Account.check_unique_fullname(field.data, current_user, parent):
            raise ValidationError(self.message)


class RequiredIfFieldEqualTo(DataRequired):
    """
    Makes a field required only if another field has a desired value.

    Parameters
    ----------
    field: str
        Name of the other field which value determines whether data is required.
    value:
        Field's value which makes data required.
    func:
        Callable that produces the field's value. Use this to postpone
        value calculation until validator is called.
    """
    def __init__(self, field, value=None, func=None, *args, **kwargs):
        self.other_field = field
        self.value = value
        self.func = func
        super().__init__(*args, **kwargs)

    def __call__(self, form, field):
        other_field = form[self.other_field]
        if self.func is not None:
            _value = self.func()
        else:
            _value = self.value
        if other_field.data == _value:
            super().__call__(form, field)


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
        validators=[RequiredIfFieldEqualTo(field='group_id', func=GetGroupId(name='Credit Card'))])
    payment = IntegerField(
        'Payment Day of Credit Card Invoice',
        validators=[RequiredIfFieldEqualTo(field='group_id', func=GetGroupId(name='Credit Card'))])
    submit = SubmitField('Create')


class AddReportForm(FlaskForm):
    name = StringField("Report Title", validators=[DataRequired()])
    genre = SelectField('Report Type', validators=[DataRequired()], choices=[(s, s) for s in genres])

    # Create nested fields for each genre choice
    information_kinds = SelectMultipleField(
        'Information Reports', choices=[(s, s) for s in information_report_kinds])

    submit = SubmitField('Create')
