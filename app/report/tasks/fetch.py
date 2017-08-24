from flask import current_app

from app import celery
from app.database import db_session, pg_session

from .common import *
from ..models import CallTable, EventTable


@celery.task
def get_call_table():
    print('collecting call table rows')
    print(current_app.config['recent_id_query'].format(row_value='call_id', select_table='c_call'))
    sql_result = pg_session.execute(
        current_app.config['recent_id_query'].format(row_value='call_id', select_table='c_call')
    )
    current_call = results_to_dict(sql_result)
    print(current_call, type(current_call), len(current_call))
    internal_result = db_session.query(CallTable.call_id).order_by(CallTable.call_id.desc()).limit(1)
    # print(internal_result, type(internal_result[0]))
    last_call = results_to_dict(internal_result)
    print(last_call)

    db_session.remove()
    pg_session.remove()
    # print('entering get_records')
    # if call_model and event_model:
    #     # Get records by date
    #     call_statement = call_model.src_statement(get_date)
    #     event_statement = event_model.src_statement(get_date)
    #
    #     # Get records for the CallTable
    #     call_data_ptr = pg_session.execute(call_statement)
    #     call_data_records = results_to_dict(call_data_ptr)  # Returns list of dicts
    #
    #     # Get records for the EventTable
    #     event_data_ptr = pg_session.execute(event_statement)
    #     event_data_records = results_to_dict(event_data_ptr)  # Returns list of dicts
    #
    #     # Convert event: records -> event model -> event
    #     event_data = [event_model(**event_record) for event_record in event_data_records]
    #
    #     for foreign_record in call_data_records:
    #         call = call_model(**foreign_record)
    #
    #         # this sucks right now
    #         for call_event in [call_event for call_event in event_data
    #                            if call_event.call_id == call.call_id]:
    #             call.add_event(call_event)
    #
    #         # Add foreign records to current session
    #         db_session.add(call)
    #     print('committing')
    #     try:
    #         db_session.commit()
    #     except IntegrityError:
    #         print('Records exist.')
    #
