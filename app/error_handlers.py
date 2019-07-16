from flask import render_template, Blueprint

from app import db

blueprint = Blueprint('error_handlers', __name__, template_folder='templates/errors')


@blueprint.app_errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@blueprint.app_errorhandler(403)
def forbidden_error(error):
    return render_template('403.html'), 403


@blueprint.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500