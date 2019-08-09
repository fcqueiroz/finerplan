from finerplan.model import GetAccountGroupId


def visa():
    return dict(
        name='Visa 3412',
        group=GetAccountGroupId(name='Credit Card'),
        closing=11,  # Day of month when the credit card invoice closes
        payment=25  # Day of month when the credit card invoice is paid
    )
