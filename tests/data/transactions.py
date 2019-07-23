from datetime import datetime
from app.models import Transaction


def first_salary():
    return Transaction(
        value=1200,
        description='Regular Salary',
        accrual_date=datetime(2019, 7, 2)
    )


def dining_out():
    return Transaction(
        value=15,
        description='Dining out',
        accrual_date=datetime(2019, 7, 4)
    )


def phone_bill():
    return Transaction(
        value=50,
        description='Phone bill',
        accrual_date=datetime(2019, 7, 25)
    )
