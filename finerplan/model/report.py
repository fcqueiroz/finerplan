from finerplan import db

from config import report_names


class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(64), nullable=False)
    group = db.Column(db.String(64), nullable=False)

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
        card_reports = db.session.query(cls).filter(cls.name.in_(card_report_names))
        card.reports.extend(card_reports)
        db.session.commit()


def extract_report_list(group, **kwargs):
    if group in report_names.keys():
        form_field_name = group.lower() + '_names'
        return kwargs.get(form_field_name)
    else:
        raise ValueError(f"Unknown group='{group}'")
