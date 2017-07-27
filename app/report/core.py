from sqlalchemy.inspection import inspect
from sqlalchemy.sql import func, and_
from flask import current_app
from app.report.sla_report import cache, sla_report
from pandas import DataFrame
from dateutil.parser import parse
from .processes import get_records


def query_by_date(session, call_table, date):
    return session.query(call_table).filter(
                and_(
                    call_table.call_direction == 1,
                    func.date(call_table.start_time) == func.date(date)
                )
            )


def query_by_range(session, call_table, start, end):
    return session.query(call_table).filter(
                and_(
                    call_table.call_direction == 1,
                    func.date(call_table.start_time) >= func.date(start),
                    func.date(call_table.start_time) <= func.date(end)
                )
            )


def get_count(query):
    if query:
        count_q = query.statement.with_only_columns([func.count()]).order_by(None)
        count = query.session.execute(count_q).scalar()
    else:
        count = 0
    return count


def meta_frame(
        page,   # Integer representing the page
        query,  # Unmodified query object
        model,  # Model used in Query
        per_page=None,
        ascending=True
):
    # Determine metadata and create mapper class
    query_model = inspect(model)

    if not per_page:
        per_page = current_app.config['ROWS_PER_PAGE']

    # Get pk from the mapper. pk is <table>.<pk name>
    pk = query_model.primary_key[0]     # this is a pk object

    # Get total before slicing
    total = get_count(query)

    # Sort order
    query = query.order_by(pk.asc()) if ascending else query.order_by(pk.desc())

    offset = (page - 1) * per_page

    # Offset if we are going beyond the initial ROWS_PER_PAGE
    if offset > 0:
        query = query.offset(offset)

    # Limit the number of rows to the page
    query = query.limit(per_page)

    frame_w_meta = {
        'total': total,
        'frame': query.frame(index_col=pk.name),
        'per_page': per_page,
        'page': page
    }
    return frame_w_meta


def run_report(query, report_range):
    # Cache consumes the events relationship of each CallTable
    cached_records = cache(query.all())

    # Run report on cached records
    results = sla_report(cached_records, list(current_app.config['CLIENTS']))
    df = DataFrame.from_items(
        [col for col in results.to_dict().items()]
    )
    df.name = 'sla_report {range}'.format(range=report_range)
    df.index = ['{ext} {name}'.format(ext=client_ext, name=client_info['CLIENT_NAME'])
                for client_ext, client_info in current_app.config['CLIENTS'].items()] + ['Summary']
    return df


def parse_date_range(date_range):
    start, end = date_range.split(' - ')
    return parse(start), parse(end)


def record_retriever(models, dates):

    CallTable = models.get('calltable')
    EventTable = models.get('eventtable')

    worker_threads = []
    for get_date in dates:
        with current_app.app_context():
            worker = get_records(CallTable, EventTable, get_date)
            worker_threads += [worker]
        print('added work')
    # worker_threads = [thread.join() for thread in worker_threads]
    print('joined threads')

    print(worker_threads)
    print('claiming I added records', flush=True)
