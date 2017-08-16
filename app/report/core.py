from sqlalchemy.inspection import inspect
from sqlalchemy.sql import func, and_
from dateutil.parser import parse

# Access app variables from module
from flask_login import current_user

# Module imports
from .models import ClientTable, ManagerClientLink, CallTable, EventTable


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
