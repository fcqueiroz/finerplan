from finerplan.model.account import AccountGroups


def turn_group_into_id(account_data):
    _name = account_data['name']
    _group = account_data['group']

    _group_id = AccountGroups.query.filter_by(name=_group).first().id
    return dict(name=_name, group_id=_group_id)


def expenses():
    return dict(
        name='Expenses',
        group='Expenses'
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
        group='Expenses'
    )


def food():
    return dict(
        name='Food',
        group='Expenses'
    )


def rent():
    return dict(
        name='Rent',
        group='Expenses'
    )


def utilities():
    return dict(
        name='Utilities',
        group='Expenses'
    )
