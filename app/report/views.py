from flask import render_template, current_app, redirect, url_for, request, g, Blueprint
from flask_login import login_required
from sqlalchemy.sql import func
from datetime import datetime

from app.core import get_redirect_target

from .models import CallTable
from .pandas_page import PandasPage
from .core import query_config

bp = Blueprint('report', __name__, template_folder='templates', static_folder='static', static_url_path='/report/static')


@bp.route('/report', methods=['GET', 'POST'])
@bp.route('/report/<int:page>', methods=['GET', 'POST'])
@login_required
def index(page=1):
    next = get_redirect_target()
    date = datetime.today().replace(day=5).date()

    query = g.session.query(CallTable).filter(func.date(date))

    panda_frame = PandasPage(
        # Logic for changing the query
        **query_config(page, query, CallTable)
    )
    panda_frame.frame.name = '07-05-2017'
    return render_template(
        'report_index.html',
        title='Report',
        next=next,
        table=panda_frame,
        tablename=panda_frame.frame.name
    )
