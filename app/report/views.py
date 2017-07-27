from flask import render_template, g, Blueprint, request, jsonify, make_response
from flask_login import login_required
from datetime import datetime, timedelta
from json import dumps, loads

# App imports
from app.core import get_redirect_target

# Module imports
from . import excel
from .models import CallTable, EventTable
# from .schemas import CallSchema
from .pandas_page import PandasPage
from .core import meta_frame, run_report, parse_date_range, record_retriever, get_count, query_by_date, query_by_range

bp = Blueprint(
    'report',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/report/static'
)


@bp.route('/report', methods=['GET', 'POST'])
@bp.route('/report/<int:page>', methods=['GET', 'POST'])
@login_required
def index(page=1):
    next = get_redirect_target()
    # report_range = request.form.get('report_range')
    # print('Entered report index', report_range)
    # print(request.method)
    # print(request.args)
    #
    # if request.method == 'POST' and report_range:
    #
    #     # Set up view query if not redirecting
    #     start, end = parse_date_range(report_range)
    #
    #     # Check if the records need to be retrieved
    #     start_date = start.date()
    #     end_date = end.date()
    #
    #     dates = []
    #     print('checking dates')
    #     while start_date <= end_date:
    #
    #         # Cheaper lookup to see if we need to get a days worth of records
    #         query = query_by_date(g.session, CallTable, start_date)
    #         total = get_count(query)
    #
    #         # Only the current day can continually update
    #         if start_date == datetime.today().date() or total == 0:
    #             print('adding retrieval date for', start_date, total)
    #             dates += [start_date]
    #
    #         start_date += timedelta(days=1)
    #
    #     if dates:
    #         print('getting some dates')
    #         # record_retriever(
    #         #     {
    #         #         CallTable.__tablename__: CallTable,
    #         #         EventTable.__tablename__: EventTable
    #         #     },
    #         #     dates
    #         # )
    #
    #     # Get request records to display
    #     print('getting records to display')
    #     query = query_by_range(g.session, CallTable, start, end)
    # else:
    #     report_range = datetime.today().replace(day=5).date()
    #     query = query_by_date(g.session, CallTable, report_range)
    #
    # # Paginated data frame
    # panda_frame = PandasPage(
    #     # Logic for changing the query
    #     **meta_frame(page, query, CallTable)
    # )
    # panda_frame.frame.name = report_range
    return render_template(
        'data_index.html',
        title='Data Gallery',
        next=next,
        # table=panda_frame,
        columns=list(CallTable.__table__.columns.keys()),
        tablename='SLA REPORT'
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
        if start == end:
            query = query_by_date(g.session, CallTable, start)
            print('got query in single value')
        else:
            query = query_by_range(g.session, CallTable, start, end)

            print('got query in multi value')
        print('got query')
    else:
        print('running else')
        report_range = datetime.today().replace(day=5).date()
        query = query_by_date(g.session, CallTable, report_range)

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


@bp.route('/download')
def export():
    return excel.make_response_from_array([[1, 2], [3, 4]], "csv")


@bp.route('/ajax', methods=['GET'])
@bp.route('/ajax/<int:page>', methods=['GET'])
def ajax(page=1):
    print('report ajax')
    report_range = request.args.get('report_range', '', type=str)
    start, end = parse_date_range(report_range)
    query = query_by_range(g.session, CallTable, start, end)

    # This will include relationships
    # call_schema = CallSchema()
    # schema_results = call_schema.dump(query, many=True).data

    # This just runs the query and is much faster
    results = query.frame().to_dict(orient='records')

    # # Paginated data frame
    # panda_frame = PandasPage(
    #     # Logic for changing the query
    #     **meta_frame(page, query, CallTable)
    # )
    return jsonify(results)
