import flask_excel as excel
from datetime import timedelta
from celery.schedules import crontab

from . import views as report_view
from .models import CallTable, EventTable, ReportCache
from .tasks.fetch import fetch_src_records
from app import app, celery

# Make excel responses
excel.init_excel(app)

# TODO remove this and integrate programmatically
# Update app settings with report settings
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

# Need to know the most recent row id
recent_id_query = """
SELECT {row_value}
FROM {select_table}
ORDER BY {row_value} DESC
LIMIT 1;
"""

get_rows_query = """
SELECT *
FROM {select_table}
WHERE {row_value} > {start_id} AND
      {row_value} <= {end_id}
ORDER BY {row_value} DESC
"""

app.config.update(
    sla_report_headers=output_headers,
    sla_default_row=default_row,
    sla_row_data=row_data,
    recent_id_query=recent_id_query,
    get_rows_query=get_rows_query
)


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls test('hello') every 10 seconds.
    # sender.add_periodic_task(10.0, test.s('hello'), name='add every 10')

    # Calls test('world') every 30 seconds
    # sender.add_periodic_task(30.0, test.s('world'), expires=10)

    # Executes every Monday morning at 7:30 a.m.
    sender.add_periodic_task(
        crontab(minute=1),
        fetch_src_records.s('call_id', 'c_call'),
    )
# celery.conf.beat_schedule = {
#     # Executes every Monday morning at 7:30 a.m.
#     'update-records-60-seconds': {
#         'task': 'app.report.tasks.fetch.fetch_src_records',
#         'schedule': ,
#         'args': ('call_id', 'c_call'),
#     },
# }
