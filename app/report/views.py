from flask import render_template, g, Blueprint, jsonify
from flask_login import login_required
from sqlalchemy.sql import func, and_, exists

from datetime import datetime

# Module imports
from . import excel
from .models import CallTable, EventTable
from .core import configure_query, parse_date_range
from .tasks.sla_report import run_report

bp = Blueprint(
    'report',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/report/static'
)


@bp.route('/report', methods=['GET', 'POST'])
@login_required
def index():
    return render_template(
        'report_template.html',
        title='Data Gallery',
        columns=list(CallTable.__table__.columns.keys())
    )


@bp.route('/report/<string:report_type>', methods=['GET', 'POST'])
@login_required
def report(report_type=''):
    output_headers = [
        'Client',
        'I/C Presented',
        'I/C Live Answered',
        'I/C Abandoned',
        'Voice Mails',
        'Incoming Live Answered (%)',
        'Incoming Received (%)',
        'Incoming Abandoned (%)',
        'Average Incoming Duration',
        'Average Wait Answered',
        'Average Wait Lost',
        'Calls Ans Within 15',
        'Calls Ans Within 30',
        'Calls Ans Within 45',
        'Calls Ans Within 60',
        'Calls Ans Within 999',
        'Call Ans + 999',
        'Longest Waiting Answered',
        'PCA'
    ]
    return render_template(
        'report_template.html',
        title='{type} Report'.format(type=report_type.upper()),
        columns=list(output_headers)
    )


@bp.route('/download')
def export():
    return excel.make_response_from_array([[1, 2], [3, 4]], "csv")


@bp.route('/api', methods=['GET'])
def api():
    print('report api')

    # Parser section
    g.parser.add_argument('start', type=int, location='args')
    g.parser.add_argument('draw', type=int, location='args')
    g.parser.add_argument('length', type=int, location='args')
    g.parser.add_argument('type', type=str, location='args')
    g.parser.add_argument('report_range', type=str, location='args')
    g.parser.add_argument('download', type=bool, location='args')
    args = g.parser.parse_args()

    # Arguments
    start, end = parse_date_range(args['report_range'])

    # Execute query
    query = g.session.query(
        CallTable,
        EventTable.event_type,
        EventTable.start_time.label('event_start_time'),
        EventTable.end_time.label('event_end_time')
    ).join(
        EventTable
    ).filter(
        and_(
            CallTable.start_time >= start,
            CallTable.end_time <= end,
            CallTable.call_direction == 1
        )
    )

    print('stop draw records', datetime.now(), flush=True)

    if args['type'] == 'report':
        print('running report', flush=True)
        frame = run_report(query)
        total = len(frame.index)
        frame.name = '{type} Report: {range}'.format(type=args['type'], range=args['report_range'])
        print('finished report', flush=True)
    else:
        # Server-side processing properties
        query, total = configure_query(query, CallTable, args)
        frame = query.frame()

    # This just runs the query and is much faster
    results = frame.to_dict(orient='split')

    return jsonify(
        draw=args['draw'],
        recordsTotal=total,
        recordsFiltered=total,
        data=results['data']
    )
