from sqlalchemy.exc import IntegrityError
from app.async import run_async
from app.database import db_session, pg_session


def results_to_dict(ptr):
    col_names = [item[0] for item in ptr._cursor_description()]
    return [dict(zip(col_names, row)) for row in ptr]   # Column: Cell pairs


@run_async
def get_records(call_model, event_model, get_date):
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
        try:
            db_session.commit()
        except IntegrityError:
            print('Records exist.')

        pg_session.remove()
        db_session.remove()
