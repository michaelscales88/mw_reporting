from sqlalchemy.inspection import inspect
from sqlalchemy.sql import func, and_, exists
from pandas import DataFrame, Series
from dateutil.parser import parse
from datetime import timedelta, datetime
from collections import OrderedDict
from multiprocessing.dummy import Pool as ThreadPool

# Access nginx.conf variables from module
from flask import current_app
from flask_login import current_user

# Module imports
from .models import ClientTable, ManagerClientLink
from .processes import chunks, make_programmatic_column, make_pyexcel_table, make_printable_table, run_filters, process_report


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
        query_params,
        ascending=False
):
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


def run_report(query):
    print('hit run_report', flush=True)

    # Mini-fy the join statement. Only care about event_type: time-interval amount
    records = OrderedDict()
    for call_record, event_record in query.all():
        events = records.get(call_record, {})
        try:
            events[event_record.event_type] += event_record.end_time - event_record.start_time
        except KeyError:
            events[event_record.event_type] = event_record.end_time - event_record.start_time
        records[call_record] = events

    # Make a pool of workers
    thread_count = current_app.config['THREAD_LIMIT']
    pool = ThreadPool(thread_count)
    record_pivot = int(len(records) / thread_count)

    print('run filters start', datetime.now(), flush=True)

    thread_results = pool.starmap(
        run_filters,
        zip(
            # OrderedDict -> List: Maintains order of original query
            chunks(list(records.items()), chunk_size=record_pivot)
        )
    )

    # close the pool and wait for the work to finish
    pool.close()
    pool.join()

    print('run filters stop', datetime.now(), flush=True)

    # This is probably inefficient
    # Flattens result lists from threads into one list
    filtered_records = []
    for thread_list in thread_results:
        filtered_records.extend(thread_list)

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
        1.0,  # 'Incoming Live Answered (%)',
        1.0,  # 'Incoming Received (%)',
        0.0,  # 'Incoming Abandoned (%)'
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
        1.0  # 'PCA'
    ]

    row_data = [
        {
            'tgt_column': 'Incoming Live Answered (%)',
            'lh_values': ('I/C Live Answered',),
            'rh_values': ('I/C Presented',)

        },
        {
            'tgt_column': 'Incoming Received (%)',
            'lh_values': ('I/C Live Answered', 'Voice Mails',),
            'rh_values': ('I/C Presented',)

        },
        {
            'tgt_column': 'Incoming Abandoned (%)',
            'lh_values': ('I/C Abandoned',),
            'rh_values': ('I/C Presented',)

        },
        {
            'tgt_column': 'Average Incoming Duration',
            'lh_values': ('Average Incoming Duration',),
            'rh_values': ('I/C Live Answered',)

        },
        {
            'tgt_column': 'Average Wait Answered',
            'lh_values': ('Average Wait Answered',),
            'rh_values': ('I/C Live Answered',)

        },
        {
            'tgt_column': 'Average Wait Lost',
            'lh_values': ('Average Wait Lost',),
            'rh_values': ('I/C Abandoned',)

        },
        {
            'tgt_column': 'PCA',
            'lh_values': ('Calls Ans Within 15', 'Calls Ans Within 30',),
            'rh_values': ('I/C Presented',)
        }
    ]

    current_report = make_pyexcel_table(output_headers, list(current_app.config['CLIENTS']), default_row)

    # Consume query data
    report = process_report(current_report, filtered_records)

    completed_report = None

    for rd in row_data:
        completed_report = make_programmatic_column(report, **rd)

    # Stringify each cell
    make_printable_table(completed_report)

    # Convert pyexcel table into dataframe
    df = DataFrame.from_items(
        [col for col in completed_report.to_dict().items()]
    )
    index = Series(['{ext} {name}'.format(ext=client_ext, name=client_info['CLIENT_NAME'])
                    for client_ext, client_info in current_app.config['CLIENTS'].items()] + ['Summary'])
    df.insert(0, "Client", index)
    return df


def parse_date_range(date_range):
    start, end = date_range.split(' - ')
    return parse(start), parse(end)


def add_client(client_name, client_id, full_service):
    new_client = ClientTable(client_name=client_name, client_id=client_id, full_service=full_service)
    current_user.add_client(new_client)
    return current_user


def remove_client(row_id):
    client = ClientTable.query.get(row_id)
    current_user.remove_client(client)
    return current_user


def delete_client(session, row_id):
    client = ClientTable.query.get(row_id)
    manager_count = session.query(ManagerClientLink).with_parent(client, 'users').count()
    print(manager_count)
    if manager_count == 0:
        # ClientTable.query.filter(ClientTable.id == row_id).delete()
        client.delete()
    else:
        print('Managers exist')
        # Check if they want to proceed
        # Remove all the relationships
        # ClientTable.query.filter(ClientTable.id == row_id).delete()
