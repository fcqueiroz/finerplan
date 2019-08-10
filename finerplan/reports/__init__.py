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
    def _get_report_creator(report_group):
        if report_group == 'Information':
            return InformationReport
        else:
            raise NotImplementedError(f"Reports of type '{report_group}' are not supported yet.")

    def _get_reports(self, card):
        _elements = []
        for report in card.reports:
            creator = self._get_report_creator(report.group)
            _elements.append(creator(report=report.name))
        return _elements

    def to_html(self):
        return '<br>'.join([el.to_html() for el in self.elements])
