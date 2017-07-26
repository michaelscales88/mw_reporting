from flask import render_template, g, Blueprint, request
from flask_login import login_required
from sqlalchemy.sql import func, and_
from datetime import datetime, timedelta

from app.core import get_redirect_target

from .models import CallTable, EventTable
from .pandas_page import PandasPage
from .core import meta_frame, run_report, parse_date_range, record_retriever, get_count

bp = Blueprint('report', __name__, template_folder='templates', static_folder='static', static_url_path='/report/static')


@bp.route('/report', methods=['GET', 'POST'])
@bp.route('/report/<int:page>', methods=['GET', 'POST'])
@login_required
def index(page=1):
    next = get_redirect_target()
    report_range = request.form.get('report_range')

    if request.method == 'POST' and report_range:

        # Set up view query if not redirecting
        start, end = parse_date_range(report_range)

        # Check if the records need to be retrieved
        start_date = start.date()
        end_date = end.date()

        dates = []
        print('checking dates')
        while start_date <= end_date:
            # Cheaper lookup to see if we need to get a days worth of records
            query = g.session.query(CallTable).filter(CallTable.start_time == func.date(start_date))
            total = get_count(query)
            print(start_date, total)
            # Only the current day can continually update
            if start_date == datetime.today().date() or total == 0:
                dates += [start_date]
                print('added a date')

            start_date += timedelta(days=1)

        if dates:
            print('getting some dates')
            record_retriever(
                g.session,
                g.foreign_session,
                {
                    CallTable.__tablename__: CallTable,
                    EventTable.__tablename__: EventTable
                },
                dates
            )

        # Get request records to display
        print('getting records to display')
        query = g.session.query(CallTable).filter(
            and_(
                CallTable.start_time >= func.date(start),
                CallTable.start_time <= func.date(end)
            )
        )
    else:
        report_range = datetime.today().replace(day=5).date()
        query = g.session.query(CallTable).filter(CallTable.start_time == func.date(report_range))

    # Paginated data frame
    panda_frame = PandasPage(
        # Logic for changing the query
        **meta_frame(page, query, CallTable)
    )
    panda_frame.frame.name = report_range
    return render_template(
        'data_index.html',
        title='Data Gallery',
        next=next,
        table=panda_frame,
        tablename=panda_frame.frame.name
    )


@bp.route('/run', methods=['GET', 'POST'])
def run():
    next = get_redirect_target()
    print('hit report.report')
    report_range = request.form.get('report_range')
    print(report_range, request.form)
    if request.method == 'POST' and report_range:
        print('report range run', report_range)
        start, end = parse_date_range(report_range)
        query = g.session.query(CallTable).filter(
            and_(
                CallTable.start_time >= func.date(start),
                CallTable.start_time <= func.date(end)
            )
        )
    else:
        print('running else')
        report_range = datetime.today().replace(day=5).date()
        query = g.session.query(CallTable.start_time == func.date(report_range))

    frame = run_report(query, report_range)

    # Paginated data frame
    panda_frame = PandasPage(
        # Logic for changing the query
        frame=frame
    )

    return render_template(
        'report.html',
        title='Report',
        next=next,
        table=panda_frame,
        tablename=panda_frame.frame.name
    )
