from .basic import InformationReport


class ReportCard(object):
    """
    This class receives a finerplan.model.Card object and
    evaluates all the reports that should be in the card.
    """
    def __init__(self, card):
        """
        card: finerplan.model.Card
            User's Card that contain the information about how to produce the card.
        """
        self.id = card.id
        self.title = card.name
        self.elements = self._get_reports(card)

    @staticmethod
    def _get_reports(card):
        return [InformationReport(report=report.name) for report in card.reports]
