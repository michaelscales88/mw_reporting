from datetime import timedelta, time
from pyexcel import Sheet
from collections import OrderedDict


def chop_microseconds(delta):
    return delta - timedelta(microseconds=delta.microseconds)


def match(record_list, match_val=None):
    matched_records = []
    # Form of bubble sort
    match_call = match_val[0]
    match_events = match_val[1]
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


def cache(call_list):
    cached_call_list = []
    for call in call_list:
        accumulator = {}
        for event in call.events:
            # Check if the event type is in the accumulator
            accumulated_events = accumulator.get(
                event.event_type,
                timedelta(0)
            )
            accumulated_events += event.end_time - event.start_time
            accumulator[event.event_type] = accumulated_events
        # Add each calls accumulated events to the call
        call_w_events = (call, accumulator)
        cached_call_list.append(call_w_events)
    return cached_call_list


def sla_report(records, client_list=None):
    print('sla_report')
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

    test_output = Sheet(
        colnames=output_headers
    )
    client_list.append('Summary')
    row_names = client_list
    try:
        for row_name in row_names:
            additional_row = OrderedDict()

            # Set default values for each row
            additional_row[str(row_name)] = [
                0,  # 'I/C Presented'
                0,  # 'I/C Live Answered'
                0,  # 'I/C Abandoned'
                0,  # 'Voice Mails'
                0,  # 'Incoming Live Answered (%)',
                0,  # 'Incoming Received (%)',
                0,  # 'Incoming Abandoned (%)'
                timedelta(0),   # 'Average Incoming Duration'
                timedelta(0),   # 'Average Wait Answered'
                timedelta(0),   # 'Average Wait Lost'
                0,  # 'Calls Ans Within 15'
                0,  # 'Calls Ans Within 30'
                0,  # 'Calls Ans Within 45'
                0,  # 'Calls Ans Within 60'
                0,  # 'Calls Ans Within 999'
                0,  # 'Call Ans + 999'
                timedelta(0),   # 'Longest Waiting Answered'
                0   # 'PCA'
            ]
            test_output.extend_rows(additional_row)
    except KeyError:
        from json import dumps
        print(dumps(client_list, indent=4))
        raise

    # Filter Step
    try:
        for x in range(0, len(records)):
            match_record = records[x]
            matches = match(records[x + 1:], match_val=match_record)
            if (
                    len(matches) > 1
                    and (match_record[0].end_time - match_record[0].start_time > timedelta(seconds=20))
                    and match_record[1].get(10, timedelta(0)) == timedelta(0)
            ):
                for a_match in matches:
                    for i, o in enumerate(records):
                        if o[0].call_id == a_match:
                            del records[i]
                            break

    except IndexError:
        # x has moved past the end of the list of remaining records
        pass

    # Process Step
    for call, events in records:
        row_name = str(call.dialed_party_number)  # This is how we bind our client user
        # print(row_name)
        # print(time(hour=7) <= call.start_time.time() <= time(hour=19))
        # print(row_name in test_output.rownames)
        if row_name in test_output.rownames and time(hour=7) <= call.start_time.time() <= time(hour=19):
            call_duration = call.end_time - call.start_time
            talking_time = events.get(4, timedelta(0))
            voicemail_time = events.get(10, timedelta(0))
            hold_time = sum(
                [events.get(event_type, timedelta(0)) for event_type in (5, 6, 7)],
                timedelta(0)
            )
            wait_duration = call_duration - talking_time - hold_time
            # DO the rest of the output work
            if talking_time > timedelta(0):
                test_output[row_name, 'I/C Presented'] += 1
                test_output[row_name, 'I/C Live Answered'] += 1
                test_output[row_name, 'Average Incoming Duration'] += talking_time
                test_output[row_name, 'Average Wait Answered'] += wait_duration

                # Adding to Summary
                test_output['Summary', 'I/C Presented'] += 1
                test_output['Summary', 'I/C Live Answered'] += 1
                test_output['Summary', 'Average Incoming Duration'] += talking_time
                test_output['Summary', 'Average Wait Answered'] += wait_duration

                # Qualify calls by duration
                if wait_duration <= timedelta(seconds=15):
                    test_output[row_name, 'Calls Ans Within 15'] += 1
                    test_output['Summary', 'Calls Ans Within 15'] += 1

                elif wait_duration <= timedelta(seconds=30):
                    test_output[row_name, 'Calls Ans Within 30'] += 1
                    test_output['Summary', 'Calls Ans Within 30'] += 1

                elif wait_duration <= timedelta(seconds=45):
                    test_output[row_name, 'Calls Ans Within 45'] += 1
                    test_output['Summary', 'Calls Ans Within 45'] += 1

                elif wait_duration <= timedelta(seconds=60):
                    test_output[row_name, 'Calls Ans Within 60'] += 1
                    test_output['Summary', 'Calls Ans Within 60'] += 1

                elif wait_duration <= timedelta(seconds=999):
                    test_output[row_name, 'Calls Ans Within 999'] += 1
                    test_output['Summary', 'Calls Ans Within 999'] += 1

                else:
                    test_output[row_name, 'Call Ans + 999'] += 1
                    test_output['Summary', 'Call Ans + 999'] += 1

                if wait_duration > test_output[row_name, 'Longest Waiting Answered']:
                    test_output[row_name, 'Longest Waiting Answered'] = wait_duration

                if wait_duration > test_output['Summary', 'Longest Waiting Answered']:
                    test_output['Summary', 'Longest Waiting Answered'] = wait_duration

            elif voicemail_time > timedelta(seconds=20):
                # if record.unique_id1 == test_client:
                #     print('I am a voice mail call', record.id)
                test_output[row_name, 'I/C Presented'] += 1
                test_output[row_name, 'Voice Mails'] += 1
                test_output[row_name, 'Average Wait Lost'] += call_duration

                test_output['Summary', 'I/C Presented'] += 1
                test_output['Summary', 'Voice Mails'] += 1
                test_output['Summary', 'Average Wait Lost'] += call_duration

            elif call_duration > timedelta(seconds=20):
                # if record.unique_id1 == test_client:
                #     print('I am a lost call', record.id)
                test_output[row_name, 'I/C Presented'] += 1
                test_output[row_name, 'I/C Abandoned'] += 1
                test_output[row_name, 'Average Wait Lost'] += call_duration

                test_output['Summary', 'I/C Presented'] += 1
                test_output['Summary', 'I/C Abandoned'] += 1
                test_output['Summary', 'Average Wait Lost'] += call_duration

            else:
                print('passed', call)
                pass

    # Finalize step
    for row_name in test_output.rownames:
        row_name = str(row_name)
        try:
            test_output[row_name, 'Incoming Live Answered (%)'] = '{0:.1%}'.format(
                test_output[row_name, 'I/C Live Answered'] / test_output[row_name, 'I/C Presented']
            )
        except ZeroDivisionError:
            test_output[row_name, 'Incoming Live Answered (%)'] = '{0:.1%}'.format(1.0)

        try:
            test_output[row_name, 'Incoming Live Answered (%)'] = '{0:.1%}'.format(
                test_output[row_name, 'I/C Live Answered'] / test_output[row_name, 'I/C Presented']
            )
        except ZeroDivisionError:
            test_output[row_name, 'Incoming Live Answered (%)'] = '{0:.1%}'.format(1.0)

        try:
            test_output[row_name, 'Incoming Received (%)'] = '{0:.1%}'.format(
                (test_output[row_name, 'I/C Live Answered'] + test_output[row_name, 'Voice Mails'])
                / test_output[row_name, 'I/C Presented']
            )
        except ZeroDivisionError:
            test_output[row_name, 'Incoming Received (%)'] = '{0:.1%}'.format(1.0)

        try:
            test_output[row_name, 'Incoming Abandoned (%)'] = '{0:.1%}'.format(
                test_output[row_name, 'I/C Abandoned'] / test_output[row_name, 'I/C Presented']
            )
        except ZeroDivisionError:
            test_output[row_name, 'Incoming Abandoned (%)'] = '{0:.1%}'.format(1.0)

        try:
            test_output[row_name, 'Average Incoming Duration'] = str(
                chop_microseconds(test_output[row_name, 'Average Incoming Duration'] / test_output[row_name, 'I/C Live Answered'])
            )
        except ZeroDivisionError:
            test_output[row_name, 'Average Incoming Duration'] = '0:00:00'

        try:
            test_output[row_name, 'Average Wait Answered'] = str(
                chop_microseconds(test_output[row_name, 'Average Wait Answered'] / test_output[row_name, 'I/C Live Answered'])
            )
        except ZeroDivisionError:
            test_output[row_name, 'Average Wait Answered'] = '0:00:00'

        try:
            test_output[row_name, 'Average Wait Lost'] = str(
                chop_microseconds(test_output[row_name, 'Average Wait Lost'] / test_output[row_name, 'I/C Abandoned'])
            )
        except ZeroDivisionError:
            test_output[row_name, 'Average Wait Lost'] = '0:00:00'

        test_output[row_name, 'Longest Waiting Answered'] = str(
            chop_microseconds(test_output[row_name, 'Longest Waiting Answered'])
        )

        try:
            test_output[row_name, 'PCA'] = '{0:.1%}'.format(
                (test_output[row_name, 'Calls Ans Within 15'] + test_output[row_name, 'Calls Ans Within 30'])
                / test_output[row_name, 'I/C Presented']
            )
        except ZeroDivisionError:
            test_output[row_name, 'PCA'] = '{0:.1%}'.format(1.0)

    return test_output
