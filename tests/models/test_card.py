import pytest

from finerplan.model import Card

from tests.data.cards import test_report


@pytest.mark.usefixtures('test_transactions')
def test_card_create(test_user):
    report_data = test_report()
    card = Card.create(user=test_user, **report_data)

    assert Card.query.count() == 1
    assert card.reports.count() == 1
    assert card.reports.one().kind == report_data['information_kinds'][0]
