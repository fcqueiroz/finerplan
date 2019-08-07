def test_report():
    return dict(
        name='Test Report',
        genre='Information',
        information_kinds=['Current Balance'])


def basic_report():
    return dict(
        name='Basic Report',
        genre='Information',
        information_kinds=[
            'Current Balance', 'Current Month Income',
            'Current Month Expenses', 'Savings Rate'])
