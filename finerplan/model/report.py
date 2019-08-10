from finerplan import db

from config import form_available_report_groups


class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(64), nullable=False)
    group = db.Column(db.String(64), nullable=False)

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.id} {self.group} {self.name}>'

    @classmethod
    def assign_to(cls, card, group, **kwargs) -> None:
        """
        Attaches the reports to a Card.

        Parameters
        ----------
        card: finerplan.model.card.Card
             Card to be assigned to the provided reports
        group: str
            Name of the Card's report group
        """
        card_report_names = extract_report_list(group, **kwargs)
        print(card_report_names)
        card_reports = db.session.query(cls).filter(cls.name.in_(card_report_names))
        card.reports.extend(card_reports)
        print(card_reports)
        db.session.commit()


def extract_report_list(group, **kwargs):
    if group in form_available_report_groups:
        form_field_name = group.lower() + '_names'
        if group == 'Information':
            return kwargs[form_field_name]
        else:
            return [kwargs[form_field_name]]
    else:
        raise ValueError(f"Unknown group='{group}'")
