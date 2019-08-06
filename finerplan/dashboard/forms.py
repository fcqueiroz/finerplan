from datetime import date

from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import DateField, DecimalField, IntegerField, RadioField, SelectField, \
    StringField, SubmitField
from wtforms.validators import DataRequired, ValidationError

from finerplan.model import Account
from finerplan.model.account import AccountGroups


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
    group_id = SelectField('Account Group', validators=[DataRequired()], choices=[], coerce=int)
    submit = SubmitField('Create')
