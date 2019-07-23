from app.models import Account


def expenses():
    return Account(
        name='Expenses'
    )


def earnings():
    return Account(
        name='Earnings'
    )


def equity():
    return Account(
        name='Equity'
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
