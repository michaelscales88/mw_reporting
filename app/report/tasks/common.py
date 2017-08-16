from string import Template
from datetime import timedelta
from collections import OrderedDict
from pyexcel import Sheet


class DeltaTemplate(Template):
    delimiter = "%"


def chop_microseconds(delta):
    return delta - timedelta(microseconds=delta.microseconds)


def results_to_dict(ptr):
    col_names = [item[0] for item in ptr._cursor_description()]
    return [dict(zip(col_names, row)) for row in ptr]   # Column: Cell pairs


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
