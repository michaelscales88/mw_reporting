from sqlalchemy.sql import func, and_
from dateutil.parser import parse
from flask_login import current_user
from sqlalchemy.orm.base import object_mapper
from sqlalchemy.orm.exc import UnmappedInstanceError
from pandas import DataFrame

# Module imports
from . import excel
from .tasks.sla_report import test
from .models import ClientTable, ManagerClientLink, CallTable, EventTable


def is_mapped(obj):
    try:
        object_mapper(obj)
    except UnmappedInstanceError:
        return False
    return True


def get_count(query):
    if query:
        count_q = query.statement.with_only_columns([func.count()]).order_by(None)
        count = query.session.execute(count_q).scalar()
    else:
        count = 0
    return count


def get_records(session, args):
    # Arguments
    start, end = parse_date_range(args['report_range'])

    query = session.query(
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
    return query


def configure_records(
        query,  # Unmodified query object
        query_params,
        ascending=False
):
    # Find ORM mapper
    for entity in query._entities:
        print(type(entity), entity)
        if is_mapped(entity):
            print('inside mapper')
            # Get PK from the mapper
            pk = entity.primary_key[0]

            # Sort order
            query = query.order_by(pk.asc()) if ascending else query.order_by(pk.desc())
            print('found mapper and sorted')
            break

    # Offset if we are going beyond the initial ROWS_PER_PAGE
    if query_params['start'] > 0:
        query = query.offset(query_params['start'])

    # Limit the number of rows to the page
    query = query.limit(query_params['length'])

    return query


def grouper(item):
    return item.start_time.month, item.start_time.day


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


def empty_frame():
    return DataFrame(), 0


def show_records(records, args):

    # Check total before slicing
    total = get_count(records)

    # Pagination
    data = configure_records(records, args)

    return data.frame(), total


def run_report(records):
    print('ran report')
    total = 0
    # print('calling run_report')
    # report_results = run_report.delay(records.all())
    # report_results.wait()
    # frame = report_results.get(timeout=1)
    # frame.name = '{type} Report: {range}'.format(type=args['action'], range=args['report_range'])
    return DataFrame(), total


def get_download():
    test_results = test.delay(1, 5)
    print('waiting', flush=True)
    test_results.wait()
    print(test_results.get(timeout=1))
    print('printed results', flush=True)
    return excel.make_response_from_array([[1, 2], [3, 4]], "csv")
