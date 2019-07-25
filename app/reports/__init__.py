"""Generates basic reports for Overview page."""

from . import basic, budget, credit_card, trends


class Report(object):
    @property
    def basic(self):
        return basic

    @property
    def budget(self):
        return budget

    @property
    def credit_card(self):
        return credit_card

    @property
    def trends(self):
        return trends
