from app.models import Transaction


def first_salary():
    return Transaction(
        value=1200,
        description='Regular Salary'
    )
