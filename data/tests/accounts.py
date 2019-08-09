from finerplan.model import AccountingGroup


def turn_group_into_id(account_data):
    _group = account_data['group']
    _group_id = AccountingGroup.query.filter_by(name=_group).first().id
    del account_data['group']
    account_data['group_id'] = _group_id
    return account_data


def expenses():
    return dict(
        name='Expenses',
        group='Expense'
    )


def income():
    return dict(
        name='Income',
        group='Income'
    )


def equity():
    return dict(
        name='Equity',
        group='Equity'
    )


def housing():
    return dict(
        name='Housing',
        group='Expense'
    )


def food():
    return dict(
        name='Food',
        group='Expense'
    )


def rent():
    return dict(
        name='Rent',
        group='Expense'
    )


def utilities():
    return dict(
        name='Utilities',
        group='Expense'
    )


def card_3412():
    return dict(
        name='Credit Card 3412',
        group='Credit Card',
        closing=11,  # Day of month when the credit card invoice closes
        payment=25  # Day of month when the credit card invoice is paid
    )


def devices():
    return dict(
        name='Electronic Devices',
        group='Expense'
    )
