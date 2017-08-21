from flask import render_template, g, Blueprint, jsonify, current_app
from flask_login import login_required

# Module imports
from .models import CallTable
from .core import get_records, get_download, show_records, run_report, empty_frame


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
        columns=list(CallTable.__table__.columns.keys()),
        iDisplayLength=current_app.config['ROWS_PER_PAGE']
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
        columns=list(output_headers),
        iDisplayLength=-1
    )


@bp.route('/api', methods=['GET'])
def api():

    # Parser section
    g.parser.add_argument('start', type=int, location='args')
    g.parser.add_argument('draw', type=int, location='args')
    g.parser.add_argument('length', type=int, location='args')
    g.parser.add_argument('action', type=str, location='args')
    g.parser.add_argument('report_range', type=str, location='args')
    args = g.parser.parse_args()

    # Draw records
    records = get_records(g.session, args)

    # Action stuff
    if args['action'] == 'report':
        frame, total = run_report(records)
    elif args['action'] == 'view':
        frame, total = show_records(records, args)
    else:
        frame, total = empty_frame()

    if args['action'] == 'download':
        get_download()

    # Separate data into the format Ajax expects
    results = frame.to_dict(orient='split')

    return jsonify(
        draw=args['draw'],
        recordsTotal=total,
        recordsFiltered=total,
        data=results['data']
    )
