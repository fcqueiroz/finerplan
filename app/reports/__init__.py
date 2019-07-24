"""Generates basic reports for Overview page."""

from . import basic, budget, credit_card


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
