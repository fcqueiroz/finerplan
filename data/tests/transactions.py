from datetime import datetime


def first_salary():
    return dict(
        value=1200,
        description='Regular Salary',
        accrual_date=datetime(2019, 7, 2)
    )


def dining_out():
    return dict(
        value=15,
        description='Dining out',
        accrual_date=datetime(2019, 7, 4)
    )


def phone_bill():
    return dict(
        value=50,
        description='Phone bill',
        accrual_date=datetime(2019, 7, 25)
    )


def computer():
    return dict(
        value=3600,
        description='High performance new Computer',
        accrual_date=datetime(2019, 6, 8),
        installments=4
    )
