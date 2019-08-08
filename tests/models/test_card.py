import pytest

from finerplan.model import Card

from tests.data.cards import test_report, basic_report


@pytest.mark.usefixtures('test_transactions')
def test_card_create(test_user):
    report_data = test_report()
    card = Card.create(user=test_user, **report_data)

    assert Card.query.count() == 1
    assert card.reports.count() == 1
    assert card.reports.one().name == report_data['information_kinds'][0]


@pytest.mark.usefixtures('test_transactions')
def test_reports_add_multiple_reports(test_user):
    """
    Tests that user can create a new report card containing multiple reports.
    """
    report_data = basic_report()
    card = Card.create(user=test_user, **report_data)

    assert card.reports.count() == 4
    for i, report in enumerate(card.reports):
        assert report.name == report_data['information_kinds'][i]
