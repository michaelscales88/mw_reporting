from sqlalchemy.inspection import inspect
from sqlalchemy.sql import func, and_, exists
from flask import current_app
from pandas import DataFrame, Series
from dateutil.parser import parse
from datetime import timedelta, datetime
from .processes import events_cache, make_pyexcel_table, make_printable_table, run_filters, process_report
from multiprocessing.dummy import Pool as ThreadPool


def query_by_range(session, call_table, start, end):
    return session.query(call_table).filter(
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

    print('hit run_report', flush=True)
    # Convert query to list of models
    records = query.all()

    # Make a pool of workers
    thread_count = current_app.config['THREAD_LIMIT']
    pool = ThreadPool(thread_count)
    record_pivot = int(len(records) / thread_count)

    print('run filters start', datetime.now(), flush=True)

    records = pool.starmap(
        run_filters,
        zip(call_table.chunks(events_cache(records), record_pivot))
    )
    # close the pool and wait for the work to finish
    pool.close()
    pool.join()

    print('run filters stop', datetime.now(), flush=True)

    output_headers = [
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

    default_row = [
        0,  # 'I/C Presented'
        0,  # 'I/C Live Answered'
        0,  # 'I/C Abandoned'
        0,  # 'Voice Mails'
        0,  # 'Incoming Live Answered (%)',
        0,  # 'Incoming Received (%)',
        0,  # 'Incoming Abandoned (%)'
        timedelta(0),  # 'Average Incoming Duration'
        timedelta(0),  # 'Average Wait Answered'
        timedelta(0),  # 'Average Wait Lost'
        0,  # 'Calls Ans Within 15'
        0,  # 'Calls Ans Within 30'
        0,  # 'Calls Ans Within 45'
        0,  # 'Calls Ans Within 60'
        0,  # 'Calls Ans Within 999'
        0,  # 'Call Ans + 999'
        timedelta(0),  # 'Longest Waiting Answered'
        0  # 'PCA'
    ]

    current_report = make_pyexcel_table(output_headers, list(current_app.config['CLIENTS']), default_row)

    # Flatten pool results
    records = [item for sublist in records for item in sublist]

    report = process_report(current_report, records)
    make_printable_table(report)

    # Convert pyexcel table into dataframe
    df = DataFrame.from_items(
        [col for col in report.to_dict().items()]
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
    # EventTable = models.get('eventtable')
    start, end = parse_date_range(dates)

    get_dates = []
    iter_date = start
    # Do a cheap lookup whether we need to get records
    while iter_date <= end:
        found = records_exist(session, CallTable, iter_date)
        if not found:
            get_dates += [iter_date.date()]
        iter_date += timedelta(days=1)

    if get_dates:
        # Make the Pool of workers
        pool = ThreadPool(current_app.config['THREAD_LIMIT'])

        # Get records from foreign database
        print('found dates', dates)
        # results = pool.starmap(get_records, zip(repeat(CallTable), repeat(EventTable), dates))

        # close the pool and wait for the work to finish
        pool.close()
        pool.join()

    query = query_by_range(session, CallTable, start, end)

    return query
