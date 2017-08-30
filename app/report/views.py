from flask import render_template, g, Blueprint, jsonify, current_app, redirect, url_for
from flask_login import login_required

# Module imports
from .models import CallTable
from .core import get_download, show_records, get_report, empty_frame, test_record_getter

bp = Blueprint(
    'report',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/report/static'
)


@bp.route('/fill', methods=['GET'])
def fill():
    test_record_getter()
    return redirect(url_for('.index'))


@bp.route('/view', methods=['GET', 'POST'])
@login_required
def index():
    return render_template(
        'report_template.html',
        title='Data Gallery',
        columns=list(CallTable.__table__.columns.keys()),
        iDisplayLength=current_app.config['ROWS_PER_PAGE'],
        page='view'
    )


@bp.route('/report', methods=['GET'])
@bp.route('/report/<string:report_type>', methods=['GET', 'POST'])
@login_required
def report(report_type='SLA'):
    return render_template(
        'report_template.html',
        title='{type} Report'.format(type=report_type.upper()),
        columns=['Client'] + current_app.config['sla_report_headers'],
        iDisplayLength=-1,
        page='report'
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

    # Action stuff
    if args['action'] == 'report':
        # Celery worker will draw records
        print('getting report')
        frame, total = get_report(g.session, args)
    elif args['action'] == 'view':
        # Draw records
        print('getting records')
        frame, total = show_records(g.session, args)
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
