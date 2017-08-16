from sqlalchemy.exc import IntegrityError
from datetime import timedelta, time, datetime
from pyexcel import Sheet
from collections import OrderedDict
from app.database import db_session  # pg_session
# from operator import add
# from functools import reduce


# def results_to_dict(ptr):
#     col_names = [item[0] for item in ptr._cursor_description()]
#     return [dict(zip(col_names, row)) for row in ptr]   # Column: Cell pairs
#
#
# def chunks(l, chunk_size=1):
#     """Yield successive chunk_size-d chunks from l."""
#     for i in range(0, len(l), chunk_size):
#         yield l[i:i + chunk_size]


# def make_programmatic_column(report, tgt_column='', lh_values=(), rh_values=()):
#     # Iterators can use next
#     rows = iter(report.rownames)
#
#     def programmed_column(cell):
#         # Get the next row on subsequent calls
#         tgt_row = next(rows)
#         # Reduce avoids handling int vs timedelta addition
#         numerator = reduce(add, [report[tgt_row, lh_value] for lh_value in lh_values])
#         denominator = reduce(add, [report[tgt_row, rh_value] for rh_value in rh_values])
#         try:
#             cell = numerator / denominator
#         except ZeroDivisionError:
#             pass
#
#         return cell
#
#     report.column.format(tgt_column, programmed_column)
#     return report


def get_records(call_model, event_model, get_date):
    print('entering get_records')
    if call_model and event_model:
        # Get records by date
        call_statement = call_model.src_statement(get_date)
        event_statement = event_model.src_statement(get_date)

        # Get records for the CallTable
        call_data_ptr = pg_session.execute(call_statement)
        call_data_records = results_to_dict(call_data_ptr)  # Returns list of dicts

        # Get records for the EventTable
        event_data_ptr = pg_session.execute(event_statement)
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
            db_session.add(call)
        print('committing')
        try:
            db_session.commit()
        except IntegrityError:
            print('Records exist.')

        pg_session.remove()
        db_session.remove()


# def chop_microseconds(delta):
#     return delta - timedelta(microseconds=delta.microseconds)


# def make_pyexcel_table(headers, row_names, default_row, with_summary=False):
#
#     report_construct = Sheet(
#         colnames=headers
#     )
#
#     row_names = list(row_names)
#
#     if with_summary:
#         row_names += ['Summary']
#
#     for row_name in row_names:
#         additional_row = OrderedDict()
#
#         # Set default values for each row
#         additional_row[str(row_name)] = default_row
#         report_construct.extend_rows(additional_row)
#
#     return report_construct


def run_filters(records):
    # print('my record', len(records), flush=True)
    print(records)
    # print(records[0][0].call_id, records[-1][0].call_id, flush=True)
    # reversed_records = reversed(records)
    # for record in reversed_records:
    #     next_record = next(reversed_records)
    #     matched = record[0].dialed_party_number == next_record[0].dialed_party_number
    #     if matched:
    #         print('found matching call', record[0].call_id)
    #         if (record[0].start_time - next_record[0].end_time) < timedelta(seconds=20):
    #             print('found duplicate', record[0].call_id)
    #             del record
    #             print('deleted record')
    # # for x in range(0, len(records)):
    #     # match_record = records[x]
    #     # matches = match(records[x + 1:], match_val=match_record)
    #     # if (
    #     #         len(matches) > 1
    #     #         and (match_record[0].end_time - match_record[0].start_time > timedelta(seconds=20))
    #     #         and match_record[1].get(10, timedelta(0)) == timedelta(0)
    #     # ):
    #     #     print(matches)
    #         # TODO this is the spot that is inefficient
    #         # for a_match in matches:
    #         #     print(a_match)
    #             # for i, o in enumerate(records):
    #             #     if o[0].call_id == a_match:
    #             #         print('removing record id for', records[i])
    #             #         del records[i]
    #             #         break
    # print('returning records')
    # print(list(reversed_records))
    return records


# def strfdelta(tdelta, fmt):
#     d = {"D": tdelta.days}
#     d["H"], rem = divmod(tdelta.seconds, 3600)
#     d["M"], d["S"] = divmod(rem, 60)
#     d = {k: '{0:02d}'.format(v) for k, v in d.items()}
#     t = DeltaTemplate(fmt)
#     return t.substitute(**d)
#
#
# def format_table(v):
#     if isinstance(v, (int, str)):
#         v = str(v)
#     elif isinstance(v, timedelta):
#         v = strfdelta(v, '%D days %H:%M:%S' if v > timedelta(days=1) else '%H:%M:%S')
#     elif isinstance(v, float):
#         v = '{0:.1%}'.format(v)
#     return v


# def process_report(in_process_report, records):
#     for call, events in records:
#
#         # Dialed party number is the client
#         row_name = str(call.dialed_party_number)
#
#         if row_name in in_process_report.rownames and time(hour=7) <= call.start_time.time() <= time(hour=19):
#             call_duration = call.end_time - call.start_time
#             talking_time = events.get(4, timedelta(0))
#             voicemail_time = events.get(10, timedelta(0))
#             hold_time = sum(
#                 [events.get(event_type, timedelta(0)) for event_type in (5, 6, 7)],
#                 timedelta(0)
#             )
#             wait_duration = call_duration - talking_time - hold_time
#
#             # A live-answered call has > 0 seconds of agent talking time
#             if talking_time > timedelta(0):
#                 in_process_report[row_name, 'I/C Presented'] += 1
#                 in_process_report[row_name, 'I/C Live Answered'] += 1
#                 in_process_report[row_name, 'Average Incoming Duration'] += talking_time
#                 in_process_report[row_name, 'Average Wait Answered'] += wait_duration
#
#                 # Qualify calls by duration
#                 if wait_duration <= timedelta(seconds=15):
#                     in_process_report[row_name, 'Calls Ans Within 15'] += 1
#
#                 elif wait_duration <= timedelta(seconds=30):
#                     in_process_report[row_name, 'Calls Ans Within 30'] += 1
#
#                 elif wait_duration <= timedelta(seconds=45):
#                     in_process_report[row_name, 'Calls Ans Within 45'] += 1
#
#                 elif wait_duration <= timedelta(seconds=60):
#                     in_process_report[row_name, 'Calls Ans Within 60'] += 1
#
#                 elif wait_duration <= timedelta(seconds=999):
#                     in_process_report[row_name, 'Calls Ans Within 999'] += 1
#
#                 else:
#                     in_process_report[row_name, 'Call Ans + 999'] += 1
#
#                 if wait_duration > in_process_report[row_name, 'Longest Waiting Answered']:
#                     in_process_report[row_name, 'Longest Waiting Answered'] = wait_duration
#
#             # A voice mail is not live answered and last longer than 20 seconds
#             elif voicemail_time > timedelta(seconds=20):
#                 in_process_report[row_name, 'I/C Presented'] += 1
#                 in_process_report[row_name, 'Voice Mails'] += 1
#                 in_process_report[row_name, 'Average Wait Lost'] += call_duration
#
#             # An abandoned call is not live answered and last longer than 20 seconds
#             elif call_duration > timedelta(seconds=20):
#                 in_process_report[row_name, 'I/C Presented'] += 1
#                 in_process_report[row_name, 'I/C Abandoned'] += 1
#                 in_process_report[row_name, 'Average Wait Lost'] += call_duration
#
#     return in_process_report


# def make_printable_table(raw_format_table):
#     raw_format_table.map(format_table)
#     return raw_format_table


def match(record_list, match_val=None):
    matched_records = []
    # Form of bubble sort
    match_call = match_val[0]
    match_events = match_val[1]
    # print(record_list[0])
    for call, call_events in record_list:
        # Check match conditions

        # If there are no 4 events then the call was not answered by a person
        match0 = (
            match_events.get(4, timedelta(0))
            == call_events.get(4, timedelta(0))
            == timedelta(0)
        )
        # If it's an unanswered call, see if it's from the same number for same client
        match1 = match_call.dialed_party_number == call.dialed_party_number
        match2 = match_call.calling_party_number == call.calling_party_number
        match3 = (call.start_time - match_call.end_time) < timedelta(seconds=61)

        all_matched = all(
            [
                match0,
                match1,
                match2,
                match3
            ]
        )

        if all_matched:
            matched_records.append(call.call_id)

    return matched_records


# def sla_report(records, call_table, client_list=None):
#     output_headers = [
#         'I/C Presented',
#         'I/C Live Answered',
#         'I/C Abandoned',
#         'Voice Mails',
#         'Incoming Live Answered (%)',
#         'Incoming Received (%)',
#         'Incoming Abandoned (%)',
#         'Average Incoming Duration',
#         'Average Wait Answered',
#         'Average Wait Lost',
#         'Calls Ans Within 15',
#         'Calls Ans Within 30',
#         'Calls Ans Within 45',
#         'Calls Ans Within 60',
#         'Calls Ans Within 999',
#         'Call Ans + 999',
#         'Longest Waiting Answered',
#         'PCA'
#     ]
#
#     test_output = Sheet(
#         colnames=output_headers
#     )
#     row_names = list(client_list)
#     # row_names += ['Summary']
#     for row_name in row_names:
#         additional_row = OrderedDict()
#
#         # Set default values for each row
#         additional_row[str(row_name)] = [
#             0,  # 'I/C Presented'
#             0,  # 'I/C Live Answered'
#             0,  # 'I/C Abandoned'
#             0,  # 'Voice Mails'
#             0,  # 'Incoming Live Answered (%)',
#             0,  # 'Incoming Received (%)',
#             0,  # 'Incoming Abandoned (%)'
#             timedelta(0),  # 'Average Incoming Duration'
#             timedelta(0),  # 'Average Wait Answered'
#             timedelta(0),  # 'Average Wait Lost'
#             0,  # 'Calls Ans Within 15'
#             0,  # 'Calls Ans Within 30'
#             0,  # 'Calls Ans Within 45'
#             0,  # 'Calls Ans Within 60'
#             0,  # 'Calls Ans Within 999'
#             0,  # 'Call Ans + 999'
#             timedelta(0),  # 'Longest Waiting Answered'
#             0  # 'PCA'
#         ]
#         test_output.extend_rows(additional_row)
#
#     # Filter Step
#     print('start filter', datetime.now(), flush=True)
#     # Convert record ids into actual records /w cached events
#     # records = [call_table.cache(call_table.query.get(record_id)) for record_id in records]
#     try:
#         for x in range(0, len(records)):
#             match_record = records[x]
#             matches = match(records[x + 1:], match_val=match_record)
#             if (
#                     len(matches) > 1
#                     and (match_record[0].end_time - match_record[0].start_time > timedelta(seconds=20))
#                     and match_record[1].get(10, timedelta(0)) == timedelta(0)
#             ):
#                 for a_match in matches:
#                     for i, o in enumerate(records):
#                         if o[0].call_id == a_match:
#                             print('deleting', records[i])
#                             del records[i]
#                             break
#
#     except IndexError:
#         # x has moved past the end of the list of remaining records
#         pass
#     # print(len(records), records[0])
#     print('stop filter', datetime.now(), flush=True)
#
#     print('start process', datetime.now(), flush=True)
#     # Process Step
#     for call, events in records:
#         # print(call)
#         # print(events)
#         row_name = str(call.dialed_party_number)  # This is how we bind our client user
#         # print(row_name)
#         # print(time(hour=7) <= call.start_time.time() <= time(hour=19))
#         # print(row_name in test_output.rownames)
#         if row_name in test_output.rownames and time(hour=7) <= call.start_time.time() <= time(hour=19):
#             call_duration = call.end_time - call.start_time
#             talking_time = events.get(4, timedelta(0))
#             voicemail_time = events.get(10, timedelta(0))
#             hold_time = sum(
#                 [events.get(event_type, timedelta(0)) for event_type in (5, 6, 7)],
#                 timedelta(0)
#             )
#             wait_duration = call_duration - talking_time - hold_time
#             # DO the rest of the output work
#             if talking_time > timedelta(0):
#                 test_output[row_name, 'I/C Presented'] += 1
#                 test_output[row_name, 'I/C Live Answered'] += 1
#                 test_output[row_name, 'Average Incoming Duration'] += talking_time
#                 test_output[row_name, 'Average Wait Answered'] += wait_duration
#
#                 # Adding to Summary
#                 # test_output['Summary', 'I/C Presented'] += 1
#                 # test_output['Summary', 'I/C Live Answered'] += 1
#                 # test_output['Summary', 'Average Incoming Duration'] += talking_time
#                 # test_output['Summary', 'Average Wait Answered'] += wait_duration
#
#                 # Qualify calls by duration
#                 if wait_duration <= timedelta(seconds=15):
#                     test_output[row_name, 'Calls Ans Within 15'] += 1
#                     # test_output['Summary', 'Calls Ans Within 15'] += 1
#
#                 elif wait_duration <= timedelta(seconds=30):
#                     test_output[row_name, 'Calls Ans Within 30'] += 1
#                     # test_output['Summary', 'Calls Ans Within 30'] += 1
#
#                 elif wait_duration <= timedelta(seconds=45):
#                     test_output[row_name, 'Calls Ans Within 45'] += 1
#                     # test_output['Summary', 'Calls Ans Within 45'] += 1
#
#                 elif wait_duration <= timedelta(seconds=60):
#                     test_output[row_name, 'Calls Ans Within 60'] += 1
#                     # test_output['Summary', 'Calls Ans Within 60'] += 1
#
#                 elif wait_duration <= timedelta(seconds=999):
#                     test_output[row_name, 'Calls Ans Within 999'] += 1
#                     # test_output['Summary', 'Calls Ans Within 999'] += 1
#
#                 else:
#                     test_output[row_name, 'Call Ans + 999'] += 1
#                     # test_output['Summary', 'Call Ans + 999'] += 1
#
#                 if wait_duration > test_output[row_name, 'Longest Waiting Answered']:
#                     test_output[row_name, 'Longest Waiting Answered'] = wait_duration
#
#                 # if wait_duration > test_output['Summary', 'Longest Waiting Answered']:
#                 #     test_output['Summary', 'Longest Waiting Answered'] = wait_duration
#
#             elif voicemail_time > timedelta(seconds=20):
#                 # if record.unique_id1 == test_client:
#                 #     print('I am a voice mail call', record.id)
#                 test_output[row_name, 'I/C Presented'] += 1
#                 test_output[row_name, 'Voice Mails'] += 1
#                 test_output[row_name, 'Average Wait Lost'] += call_duration
#
#                 # test_output['Summary', 'I/C Presented'] += 1
#                 # test_output['Summary', 'Voice Mails'] += 1
#                 # test_output['Summary', 'Average Wait Lost'] += call_duration
#
#             elif call_duration > timedelta(seconds=20):
#                 test_output[row_name, 'I/C Presented'] += 1
#                 test_output[row_name, 'I/C Abandoned'] += 1
#                 test_output[row_name, 'Average Wait Lost'] += call_duration
#
#                 # test_output['Summary', 'I/C Presented'] += 1
#                 # test_output['Summary', 'I/C Abandoned'] += 1
#                 # test_output['Summary', 'Average Wait Lost'] += call_duration
#
#             else:
#                 # print('passed', call)
#                 pass
#     print('stop process', datetime.now(), flush=True)
#
#     print('start finalize', datetime.now(), flush=True)
#
#     # Finalize step
#     for row_name in test_output.rownames:
#         row_name = str(row_name)
#         try:
#             test_output[row_name, 'Incoming Live Answered (%)'] = '{0:.1%}'.format(
#                 test_output[row_name, 'I/C Live Answered'] / test_output[row_name, 'I/C Presented']
#             )
#         except ZeroDivisionError:
#             test_output[row_name, 'Incoming Live Answered (%)'] = '{0:.1%}'.format(1.0)
#
#         try:
#             test_output[row_name, 'Incoming Live Answered (%)'] = '{0:.1%}'.format(
#                 test_output[row_name, 'I/C Live Answered'] / test_output[row_name, 'I/C Presented']
#             )
#         except ZeroDivisionError:
#             test_output[row_name, 'Incoming Live Answered (%)'] = '{0:.1%}'.format(1.0)
#
#         try:
#             test_output[row_name, 'Incoming Received (%)'] = '{0:.1%}'.format(
#                 (test_output[row_name, 'I/C Live Answered'] + test_output[row_name, 'Voice Mails'])
#                 / test_output[row_name, 'I/C Presented']
#             )
#         except ZeroDivisionError:
#             test_output[row_name, 'Incoming Received (%)'] = '{0:.1%}'.format(1.0)
#
#         try:
#             test_output[row_name, 'Incoming Abandoned (%)'] = '{0:.1%}'.format(
#                 test_output[row_name, 'I/C Abandoned'] / test_output[row_name, 'I/C Presented']
#             )
#         except ZeroDivisionError:
#             test_output[row_name, 'Incoming Abandoned (%)'] = '{0:.1%}'.format(1.0)
#
#         try:
#             test_output[row_name, 'Average Incoming Duration'] = str(
#                 chop_microseconds(test_output[row_name, 'Average Incoming Duration'] / test_output[row_name, 'I/C Live Answered'])
#             )
#         except ZeroDivisionError:
#             test_output[row_name, 'Average Incoming Duration'] = '0:00:00'
#         except TypeError:
#             print(row_name, test_output[row_name, 'Average Incoming Duration'], test_output[row_name, 'I/C Live Answered'])
#             raise
#
#         # print(test_output[row_name, 'Average Wait Answered'])
#         try:
#             test_output[row_name, 'Average Wait Answered'] = str(
#                 chop_microseconds(test_output[row_name, 'Average Wait Answered'] / test_output[row_name, 'I/C Live Answered'])
#             )
#         except ZeroDivisionError:
#             test_output[row_name, 'Average Wait Answered'] = '0:00:00'
#
#         try:
#             test_output[row_name, 'Average Wait Lost'] = str(
#                 chop_microseconds(test_output[row_name, 'Average Wait Lost'] / test_output[row_name, 'I/C Abandoned'])
#             )
#         except ZeroDivisionError:
#             test_output[row_name, 'Average Wait Lost'] = '0:00:00'
#
#         test_output[row_name, 'Longest Waiting Answered'] = str(
#             chop_microseconds(test_output[row_name, 'Longest Waiting Answered'])
#         )
#
#         try:
#             test_output[row_name, 'PCA'] = '{0:.1%}'.format(
#                 (test_output[row_name, 'Calls Ans Within 15'] + test_output[row_name, 'Calls Ans Within 30'])
#                 / test_output[row_name, 'I/C Presented']
#             )
#         except ZeroDivisionError:
#             test_output[row_name, 'PCA'] = '{0:.1%}'.format(1.0)
#     print('stop finalize', datetime.now(), flush=True)
#     return test_output
