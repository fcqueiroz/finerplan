from .basic import InformationReport, TableReport


class ReportCard(object):
    """
    This class receives a finerplan.model.Card object and
    evaluates all the reports that should be in the card.
    """
    _default_information_size = "col-12 col-md-6 col-xl-4 py-3"
    _default_table_size = "col-12 py-3"

    def __init__(self, card):
        """
        card: finerplan.model.Card
            User's Card that contain the information about how to produce the card.
        """
        self.id = card.id
        self.title = card.name
        self.elements = self._get_reports(card)
        # self.sizes = getattr(card, 'sizes', sizes)

    @staticmethod
    def _get_report_creator(report_group):
        if report_group == 'Information':
            return InformationReport
        elif report_group == 'Table':
            return TableReport
        else:
            raise NotImplementedError(f"Reports of type '{report_group}' are not supported yet.")

    def _set_size(self, report_group):
        if report_group == 'Table':
            self.sizes = self._default_table_size
        else:
            self.sizes = self._default_information_size

    def _get_reports(self, card):
        _elements = []
        for report in card.reports:
            self._set_size(report.group)
            creator = self._get_report_creator(report.group)
            _elements.append(creator(report=report.name))
        return _elements

    def to_html(self):
        return '<br>'.join([el.to_html() for el in self.elements])
