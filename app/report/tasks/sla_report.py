from flask import current_app
from pandas import DataFrame, Series
from app import celery
from datetime import time
from operator import add
from functools import reduce

from .common import *

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


@celery.task
def run_report(query):
    print('hit run_report', flush=True)

    # Create a pyexcel table with the appropriate defaults by column name
    prepared_report = make_pyexcel_table(output_headers, list(current_app.config['CLIENTS']), default_row)

    print('prepared report', flush=True)

    # Index the query. Group columns from EventTable (c_event) to the call from CallTable (c_call)
    cached_results = prepare_records(query.all())
    print('waiting cache', flush=True)
    print('cached results', flush=True)

    # Consume query data
    report = process_report(prepared_report, cached_results)
    print('process waiting', flush=True)
    print('processed results', flush=True)

    for rd in row_data:
        make_programmatic_column(report, **rd)

    # Stringify each cell
    format_table(report)

    # Convert pyexcel table into dataframe
    df = DataFrame.from_items(
        [col for col in report.to_dict().items()]
    )
    index = Series(['{ext} {name}'.format(ext=client_ext, name=client_info['CLIENT_NAME'])
                    for client_ext, client_info in current_app.config['CLIENTS'].items()] + ['Summary'])
    df.insert(0, "Client", index)
    return df


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
    # return report


def prepare_records(record_list):
    """
    Group calls by event type on the Event Table
    Use the grouped event types to give the call properties
    E.g. Interval of 0 for event type 4 means that the call never had Talking time == Unanswered call
    :param record_list: 
    :return: OrderedDict. Key: CallTable Values: Sum of intervals grouped by event type
    """
    cached_results = OrderedDict()
    for call, event_type, start, end in record_list:

        cached_result = cached_results.get(call)

        if cached_result:
            # Get the event_type from the call
            cached_event = cached_result.get(event_type)

            # Update or create the event for the call
            if cached_event:
                cached_event += end - start
            else:
                cached_event = end - start

            cached_result[event_type] = cached_event
        else:
            # Create a cache if one does not exist
            cached_result = {
                event_type: end - start
            }

        # Update the cached results with the accumulated event
        cached_results[call] = cached_result
    return cached_results


def process_report(in_process_report, records):
    for call, events in records.items():

        # Dialed party number is the client
        row_name = str(call.dialed_party_number)

        if row_name in in_process_report.rownames and time(hour=7) <= call.start_time.time() <= time(hour=19):
            call_duration = call.end_time - call.start_time
            talking_time = events.get(4, timedelta(0))
            voicemail_time = events.get(10, timedelta(0))
            hold_time = sum(
                [events.get(event_type, timedelta(0)) for event_type in (5, 6, 7)],
                timedelta(0)
            )
            wait_duration = call_duration - talking_time - hold_time

            # A live-answered call has > 0 seconds of agent talking time
            if talking_time > timedelta(0):
                in_process_report[row_name, 'I/C Presented'] += 1
                in_process_report[row_name, 'I/C Live Answered'] += 1
                in_process_report[row_name, 'Average Incoming Duration'] += talking_time
                in_process_report[row_name, 'Average Wait Answered'] += wait_duration

                # Qualify calls by duration
                if wait_duration <= timedelta(seconds=15):
                    in_process_report[row_name, 'Calls Ans Within 15'] += 1

                elif wait_duration <= timedelta(seconds=30):
                    in_process_report[row_name, 'Calls Ans Within 30'] += 1

                elif wait_duration <= timedelta(seconds=45):
                    in_process_report[row_name, 'Calls Ans Within 45'] += 1

                elif wait_duration <= timedelta(seconds=60):
                    in_process_report[row_name, 'Calls Ans Within 60'] += 1

                elif wait_duration <= timedelta(seconds=999):
                    in_process_report[row_name, 'Calls Ans Within 999'] += 1

                else:
                    in_process_report[row_name, 'Call Ans + 999'] += 1

                if wait_duration > in_process_report[row_name, 'Longest Waiting Answered']:
                    in_process_report[row_name, 'Longest Waiting Answered'] = wait_duration

            # A voice mail is not live answered and last longer than 20 seconds
            elif voicemail_time > timedelta(seconds=20):
                in_process_report[row_name, 'I/C Presented'] += 1
                in_process_report[row_name, 'Voice Mails'] += 1
                in_process_report[row_name, 'Average Wait Lost'] += call_duration

            # An abandoned call is not live answered and last longer than 20 seconds
            elif call_duration > timedelta(seconds=20):
                in_process_report[row_name, 'I/C Presented'] += 1
                in_process_report[row_name, 'I/C Abandoned'] += 1
                in_process_report[row_name, 'Average Wait Lost'] += call_duration

    return in_process_report
