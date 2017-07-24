from sqlalchemy.inspection import inspect
from sqlalchemy.sql import func
from flask import current_app


def get_count(query):
    if query:
        count_q = query.statement.with_only_columns([func.count()]).order_by(None)
        count = query.session.execute(count_q).scalar()
    else:
        count = 0
    return count


def query_config(page, query, model, ascending=True):
    # Determine metadata
    query_model = inspect(model)
    pk = query_model.primary_key[0]

    # Get total before slicing
    total = get_count(query)

    # Sort order
    query = query.order_by(pk.asc()) if ascending else query.order_by(pk.desc())

    offset = (page - 1) * current_app.config['ROWS_PER_PAGE']

    # Offset if we are going beyond the initial ROWS_PER_PAGE
    if offset > 0:
        query = query.offset(offset)

    # Limit the number of rows to the page
    query = query.limit(current_app.config['ROWS_PER_PAGE'])

    frame_w_meta = {
        'total': total,
        'frame': query.frame(index_col='call_id'),
        'per_page': current_app.config['ROWS_PER_PAGE'],
        'page': page
    }
    return frame_w_meta
