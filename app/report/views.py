from flask import render_template, flash, redirect, url_for, request, g, Blueprint
from flask_login import login_required

from app.core import get_redirect_target

# from .model import User


bp = Blueprint('report', __name__, template_folder='templates', static_folder='static', static_url_path='/report/static')


@bp.route('/report', methods=['GET', 'POST'])
@login_required
def index():
    next = get_redirect_target()

    return render_template(
        'report_index.html',
        title='Report',
        next=next
    )
