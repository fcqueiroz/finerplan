from app.models import Account


def expenses():
    return Account(
        name='Expenses'
    )


def earnings():
    return Account(
        name='Earnings'
    )


def assets():
    return Account(
        name='Assets'
    )


def liabilities():
    return Account(
        name='Liabilities'
    )


def housing():
    return Account(
        name='Housing',
        parent_account=expenses()
    )


def food():
    return Account(
        name='Food',
        parent_account=expenses()
    )


def rent():
    return Account(
        name='Rent',
        parent_account=housing()
    )


def utilities():
    return Account(
        name='Utilities',
        parent_account=housing()
    )


all_accounts = [expenses(), earnings(), assets(), liabilities(), housing(), food(), rent(), utilities()]
