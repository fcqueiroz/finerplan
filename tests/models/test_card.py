import pytest

from finerplan.model import Card

from tests.data.cards import new_report


@pytest.mark.usefixtures('test_transactions')
def test_card_create(test_user):
    card = Card.create(user=test_user, **new_report())

    assert Card.query.count() == 1
    assert card.reports.count() == 1
    assert card.reports.one().kind == 'current_balance'
