"""
Custom validators to user together with wtforms
"""

from flask_login import current_user
from wtforms.validators import DataRequired, ValidationError, Optional

from finerplan.model import Account


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


class CompareOtherField(object):
    """
    Base class for creating validators that depend on other field's value to be called.
    """
    def __init__(self, field, value=None, delayed=None, *args, **kwargs):
        """
        Parameters
        ----------
        field: str
            Name of the other field which value determines how data is validated.
        value:
            Other field's value which triggers data validation.
        delayed:
            Callable that produces the other field's comparison value. Use this
            to postpone value calculation until validator is called.
        """
        self._other_field = field

        if delayed is not None:
            self._delayed = delayed
        elif value is not None:
            self._other_value = value
        else:
            raise ValueError("Either 'delayed' or 'value' parameters should be set.")

        super().__init__(*args, **kwargs)

    def get_comparison_value(self):
        if hasattr(self, '_delayed'):
            return self._delayed()
        else:
            return self._other_value

    def get_form_value(self, form):
        other_field = form[self._other_field]
        return other_field.data


class RequiredIfFieldEqualTo(CompareOtherField, DataRequired):
    """
    Makes a field required only if another field has a desired value.
    """
    def __call__(self, form, field):
        form_value = self.get_form_value(form)
        comparison_value = self.get_comparison_value()

        if form_value == comparison_value:
            super().__call__(form, field)


class OptionalIfFieldDifferentThan(CompareOtherField, Optional):
    """
    Makes a field optional only if another field doesn't have a desired value.
    """
    def __call__(self, form, field):
        form_value = self.get_form_value(form)
        comparison_value = self.get_comparison_value()

        if form_value != comparison_value:
            super().__call__(form, field)
