from pandas import DataFrame, Series
from flask import current_app

# Module imports
from . import excel
from .tasks.sla_report import (
    get_count, report_task, parse_date_range,
    get_mapped_class, get_records, get_cached_report,
    report_exists
)


def server_side_processing(
        query,  # Unmodified query object
        query_params,
        ascending=False
):
    entity = get_mapped_class(query)
    if entity:
        # Find ORM mapper
        pk = entity.primary_key[0]

        # Sort order
        query = query.order_by(pk.asc()) if ascending else query.order_by(pk.desc())

    # Offset if we are going beyond the initial ROWS_PER_PAGE
    if query_params['start'] > 0:
        query = query.offset(query_params['start'])

    # Limit the number of rows to the page
    query = query.limit(query_params['length'])

    return query


def empty_frame():
    return DataFrame(), 0


def show_records(session, args):

    # Arguments
    start, end = parse_date_range(args['report_range'])

    records = get_records(session, start, end)

    # Check total before slicing
    total = get_count(records)

    # Pagination
    data = server_side_processing(records, args)

    return data.frame(), total


def get_report(session, args):

    # Arguments
    start, end = parse_date_range(args['report_range'])

    exists = report_exists(session, start, end, 'sla_report')

    if exists:
        # No work to do
        success = True
    else:
        # Celery worker
        task_results = report_task.delay(start, end)
        task_results.wait()
        success = task_results.get(timeout=1)

    if success:
        cached_results = get_cached_report(session, start, end, 'sla_report')

        frame = DataFrame.from_dict(
            cached_results.report
        )

        frame.name = '{rpt} {frm} {to}'.format(
            rpt=cached_results.name,
            frm=start,
            to=end
        )

        # Convert pyexcel table into dataframe
        index = Series(['{ext} {name}'.format(ext=client_ext, name=client_info['CLIENT_NAME'])
                        for client_ext, client_info in current_app.config['CLIENTS'].items()] + ['Summary'])
        frame.insert(0, "Client", index)
        total = len(index)
    else:
        frame, total = empty_frame()

    return frame, total


def get_download():
    print('printed results', flush=True)
    return excel.make_response_from_array([[1, 2], [3, 4]], "csv")
