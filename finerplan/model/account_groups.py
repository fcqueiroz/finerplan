from finerplan import db
from finerplan.lib import loans

from config import account_groups_list


class AccountGroups(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column('name', db.String(50), nullable=False)

    @property
    def installments_enumerator(self):
        """
        Returns the proper way of enumerating installments based on Account's group.
        """
        if self.name == 'Credit Card':
            return self._get_credit_card_installments
        else:
            return self._get_default_installments

    @staticmethod
    def _get_credit_card_installments(account, transaction, **kwargs):
        credit_data = dict(
            accrual_date=transaction.accrual_date,
            value=kwargs.pop('value'),
            closing_day=account.closing,
            payment_day=account.payment,
            installments=kwargs.pop('installments'))
        return loans.monthly_invoice(**credit_data)

    @staticmethod
    def _get_default_installments(transaction, **kwargs):
        basic_data = dict(
            accrual_date=transaction.accrual_date,
            value=kwargs.pop('value'))
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
