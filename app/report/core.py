from pandas import DataFrame

# Module imports
from . import excel
from .tasks.sla_report import get_count, report_task, parse_date_range, get_mapped_class, get_records


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


def run_report(args):
    print('starting task dispatch')

    # Arguments
    start, end = parse_date_range(args['report_range'])

    # Celery worker
    task_results = report_task.delay(start, end)
    task_results.wait()
    result = task_results.get(timeout=1)
    print(result)

    total = 0

    # Convert pyexcel table into dataframe
    # df = DataFrame.from_items(
    #     [col for col in report.to_dict().items()]
    # )
    # index = Series(['{ext} {name}'.format(ext=client_ext, name=client_info['CLIENT_NAME'])
    #                 for client_ext, client_info in current_app.config['CLIENTS'].items()] + ['Summary'])
    # df.insert(0, "Client", index)
    return DataFrame(), total


def get_download():
    print('printed results', flush=True)
    return excel.make_response_from_array([[1, 2], [3, 4]], "csv")
