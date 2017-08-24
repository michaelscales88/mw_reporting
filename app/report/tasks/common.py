from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.inspection import inspect
from string import Template
from datetime import timedelta
from collections import OrderedDict
from pyexcel import Sheet
from dateutil.parser import parse
from sqlalchemy.sql import func, and_
from operator import add
from functools import reduce

from ..models import CallTable, EventTable, ReportCache


class DeltaTemplate(Template):
    delimiter = "%"


def chop_microseconds(delta):
    return delta - timedelta(microseconds=delta.microseconds)


def results_to_dict(ptr):
    try:
        # PG results
        col_names = [item[0] for item in ptr._cursor_description()]
        results = ptr
    except AttributeError:
        # SQLAlchemy models
        col_names = [item['name'] for item in ptr.column_descriptions]
        results = ptr.all()
    return [dict(zip(col_names, row)) for row in results]


def chunks(l, chunk_size=1):
    """Yield successive chunk_size-d chunks from l."""
    for i in range(0, len(l), chunk_size):
        yield l[i:i + chunk_size]


def strfdelta(tdelta, fmt):
    d = {"D": tdelta.days}
    d["H"], rem = divmod(tdelta.seconds, 3600)
    d["M"], d["S"] = divmod(rem, 60)
    d = {k: '{0:02d}'.format(v) for k, v in d.items()}
    t = DeltaTemplate(fmt)
    return t.substitute(**d)


def table_formatter(v):
    if isinstance(v, (int, str)):
        v = str(v)
    elif isinstance(v, timedelta):
        v = strfdelta(v, '%D days %H:%M:%S' if v > timedelta(days=1) else '%H:%M:%S')
    elif isinstance(v, float):
        v = '{0:.1%}'.format(v)
    return v


def format_table(table):
    # Apply table formatter cell by cell
    table.map(table_formatter)
    return table


def parse_date_range(date_range):
    start, end = date_range.split(' - ')
    return parse(start), parse(end)


def make_pyexcel_table(headers, row_names, default_row, with_summary=False):

    report_construct = Sheet(
        colnames=headers
    )

    row_names = list(row_names)

    if with_summary:
        row_names += ['Summary']

    for row_name in row_names:
        additional_row = OrderedDict()

        # Set default values for each row
        additional_row[str(row_name)] = default_row
        report_construct.extend_rows(additional_row)

    return report_construct


def get_mapped_class(obj):
    for o in obj:
        if isinstance(o.__class__, DeclarativeMeta):
            # Mapped class has meta data and fn
            return inspect(o)
    else:
        return False


def get_records(session, start, end):
    return session.query(
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


def make_programmatic_column(report, tgt_column='', lh_values=(), rh_values=()):
    # Iterators can use next
    rows = iter(report.rownames)

    def programmed_column(cell):
        # Get the next row on subsequent calls
        tgt_row = next(rows)

        # Reduce avoids handling int vs timedelta addition
        numerator = reduce(add, [report[tgt_row, lh_value] for lh_value in lh_values])
        denominator = reduce(add, [report[tgt_row, rh_value] for rh_value in rh_values])
        try:
            cell = numerator / denominator
        except ZeroDivisionError:
            pass

        return cell

    report.column.format(tgt_column, programmed_column)


def get_count(query):
    if query:
        count_q = query.statement.with_only_columns([func.count()]).order_by(None)
        count = query.session.execute(count_q).scalar()
    else:
        count = 0
    return count


def report_exists(session, start, end, report):
    return session.query(
        ReportCache.id
    ).filter(
        and_(
            ReportCache.name == report,
            ReportCache.start == start,
            ReportCache.end == end
        )
    ).scalar() is not None


def cache_report(session, start, end, report):
    cached_report = ReportCache(
        name=report.name,
        report=report.dict,
        start=start,
        end=end
    )
    session.add(cached_report)


def get_cached_report(session, report_start, report_end, report_name):
    return session.query(
        ReportCache
    ).filter(
        and_(
            ReportCache.name == report_name,
            ReportCache.start == report_start,
            ReportCache.end == report_end
        )
    ).first()
