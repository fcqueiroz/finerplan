from finerplan import db

from config import account_groups_list


class AccountGroups(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column('name', db.String(50), nullable=False)


def init_account_groups():
    """
    Inserts into AccountGroups the data needed for aplication.
    """
    for group_name in account_groups_list:
        result = AccountGroups.query.filter_by(name=group_name).first()
        if result is None:
            db.session.add(AccountGroups(name=group_name))
    db.session.commit()
