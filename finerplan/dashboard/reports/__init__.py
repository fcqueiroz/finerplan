"""Generates basic reports for Overview page."""
from . import budget, credit_card, trends
from .basic import BasicReport


class Report(object):
    basic = BasicReport()

    @property
    def budget(self):
        return budget

    @property
    def credit_card(self):
        return credit_card

    @property
    def trends(self):
        return trends


genres = ['Information', 'Table', 'Graph']

information_report_kinds = {
    'Current Balance': BasicReport(kind='balance')
}
