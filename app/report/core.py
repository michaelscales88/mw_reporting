from sqlalchemy.inspection import inspect
from sqlalchemy.sql import func, and_, exists
from flask import current_app
from pandas import DataFrame, Series
from dateutil.parser import parse
from datetime import timedelta, datetime
from itertools import repeat
from .processes import get_records, sla_report
from multiprocessing.dummy import Pool as ThreadPool


def query_by_range(session, call_table, start, end):
    return session.query(call_table.call_id).filter(
        and_(
            call_table.call_direction == 1,
            func.date(call_table.start_time) >= func.date(start),
            func.date(call_table.start_time) <= func.date(end)
        )
    )


def records_exist(session, table, date):
    return session.query(exists().where(func.date(table.start_time) == func.date(date))).scalar()


def get_count(query):
    if query:
        count_q = query.statement.with_only_columns([func.count()]).order_by(None)
        count = query.session.execute(count_q).scalar()
    else:
        count = 0
    return count


def configure_query(
        query,  # Unmodified query object
        model,  # Model used in Query
        query_params
):
    ascending = True
    # Determine metadata and create mapper class
    query_model = inspect(model)

    # Get pk from the mapper. pk is <table>.<pk name>
    pk = query_model.primary_key[0]  # this is a pk object

    # Get total before slicing
    total = get_count(query)

    # Sort order
    query = query.order_by(pk.asc()) if ascending else query.order_by(pk.desc())

    # Offset if we are going beyond the initial ROWS_PER_PAGE
    if query_params['start'] > 0:
        query = query.offset(query_params['start'])

    # Limit the number of rows to the page
    query = query.limit(query_params['length'])

    return query, total


def grouper(item):
    return item.start_time.month, item.start_time.day


def run_report(query, call_table):
    thread_count = current_app.config['THREAD_LIMIT']
    print('hit run_report', flush=True)
    # Make the Pool of workers
    pool = ThreadPool(thread_count)

    # All record ids for this report
    record_ids = [int(query_id[0]) for query_id in query.all()]

    # Determine number of records per thread
    record_pivot = int(len(record_ids) / thread_count)
    print('Records per thread:', record_pivot)

    print('starting report pool', flush=True)
    finished_report = pool.starmap(
        sla_report,
        zip(
            call_table.chunks(record_ids, record_pivot), repeat(call_table), repeat(list(current_app.config['CLIENTS']))
        )
    )
    # close the pool and wait for the work to finish
    pool.close()
    pool.join()
    print('finished reports', datetime.now())
    final_report = finished_report[0]
    for report in finished_report[1:]:
        final_report += report

    print(final_report)
    # Run report on cached records
    df = DataFrame.from_items(
        [col for col in final_report.to_dict().items()]
        # []
    )
    index = Series(['{ext} {name}'.format(ext=client_ext, name=client_info['CLIENT_NAME'])
                    for client_ext, client_info in current_app.config['CLIENTS'].items()] + ['Summary'])
    df.insert(0, "Client", index)
    return df


def parse_date_range(date_range):
    start, end = date_range.split(' - ')
    return parse(start), parse(end)


def get_query(session, models, dates):
    CallTable = models.get('calltable')
    EventTable = models.get('eventtable')
    start, end = parse_date_range(dates)

    # Make the Pool of workers
    pool = ThreadPool(4)

    dates = []
    iter_date = start
    # Do a cheap lookup whether we need to get records
    while iter_date <= end:
        found = records_exist(session, CallTable, iter_date)
        if not found:
            dates += [iter_date.date()]
        iter_date += timedelta(days=1)

    if dates:
        print('found dates', dates)
        results = pool.starmap(get_records, zip(repeat(CallTable), repeat(EventTable), dates))
        # close the pool and wait for the work to finish
        pool.close()
        pool.join()

    query = query_by_range(session, CallTable, start, end)
    return query
