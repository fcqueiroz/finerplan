def test_report():
    return dict(
        name='Test Report',
        group='Information',
        information_names=['Current Balance'])


def basic_report():
    return dict(
        name='Basic Report',
        group='Information',
        information_names=[
            'Current Balance', 'Current Month Income',
            'Current Month Expenses', 'Savings Rate'])
