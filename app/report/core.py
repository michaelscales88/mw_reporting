from sqlalchemy.inspection import inspect
from sqlite3 import ProgrammingError
from sqlalchemy.sql import func
from sqlalchemy.exc import IntegrityError
from flask import current_app
from app.report.sla_report import cache, sla_report
from pandas import DataFrame
from dateutil.parser import parse
from app.decorators import run_async


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


def results_to_dict(ptr):
    col_names = [item[0] for item in ptr._cursor_description()]
    return [dict(zip(col_names, row)) for row in ptr]   # Column: Cell pairs


def record_retriever(session, foreign_session, models, dates):

    CallTable = models.get('calltable')
    EventTable = models.get('eventtable')

    worker_threads = []
    for get_date in dates:
        worker = get_records(session, foreign_session, CallTable, EventTable, get_date)
        worker_threads += [worker]
    worker_threads = [thread.join() for thread in worker_threads]
    print('joined threads')

    print(worker_threads)
    # session.commit()
    # foreign_session.remove()
    print('claiming I added records', flush=True)


@run_async
def get_records(session, foreign_session, call_model, event_model, get_date):
    if call_model and event_model:
        # Get records by date
        call_statement = call_model.src_statement(get_date)
        event_statement = event_model.src_statement(get_date)

        # Get records for the CallTable
        call_data_ptr = foreign_session.execute(call_statement)
        call_data_records = results_to_dict(call_data_ptr)  # Returns list of dicts

        # Get records for the EventTable
        event_data_ptr = foreign_session.execute(event_statement)
        event_data_records = results_to_dict(event_data_ptr)  # Returns list of dicts

        # Convert event: records -> event model -> event
        event_data = [event_model(**event_record) for event_record in event_data_records]

        for foreign_record in call_data_records:
            call = call_model(**foreign_record)

            # this sucks right now
            for call_event in [call_event for call_event in event_data
                               if call_event.call_id == call.call_id]:
                call.add_event(call_event)

            # Add foreign records to current session
            session.add(call)
        try:
            session.commit()
        except IntegrityError:
            print('Records exist.')
        except ProgrammingError:
            """
            sqlite3.ProgrammingError: SQLite objects created in a thread can only be used in that same thread.The object was created in thread id 123145377161216 and this is thread id 123145382416384
            Gotta fix this when there is a constraint issue TODO
            """
            print('Records exist or something with threading.')
