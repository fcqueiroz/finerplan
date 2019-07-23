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
        name='Housing'
    )


def food():
    return Account(
        name='Food'
    )


def rent():
    return Account(
        name='Rent'
    )


def utilities():
    return Account(
        name='Utilities'
    )
