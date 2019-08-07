from finerplan import db
from finerplan.lib import loans

from config import account_groups_list


class AccountGroups(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column('name', db.String(50), nullable=False)

    def calculate_installments(self, account, transaction, **kwargs):
        value = kwargs.pop('value')
        basic_data = dict(
            accrual_date=transaction.accrual_date,
            value=value)

        if self.name == 'Credit Card':
            installments = kwargs.pop('installments')
            credit_data = dict(
                closing_day=account.closing,
                payment_day=account.payment,
                installments=installments)

            return loans.monthly_invoice(**basic_data, **credit_data)
        else:
            return loans.instant_transfer(**basic_data)


def init_account_groups():
    """
    Inserts into AccountGroups the data needed for aplication.
    """
    for group_name in account_groups_list:
        result = AccountGroups.query.filter_by(name=group_name).first()
        if result is None:
            db.session.add(AccountGroups(name=group_name))
    db.session.commit()
