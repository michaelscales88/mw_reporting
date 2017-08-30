from flask import current_app

from app import celery
from app.database import db_session, pg_session

from .common import *
from ..models import CallTable, EventTable

FETCH = {
    'c_call': {
        'statement': CallTable.call_id,
        'table': CallTable
    },
    'c_event': {
        'statement': EventTable.event_id,
        'table': EventTable
    },
}


@celery.task
def fetch_src_records(row, table):
    """
    Master: Src table (elsewhere.db)
    Slave: Destination table (app.db)
    """
    try:
        master_result = pg_session.execute(
            current_app.config['recent_id_query'].format(
                row_value=row, select_table=table
            )
        )
        slave_result = db_session.query(
            FETCH[table]['statement']
        ).order_by(
            FETCH[table]['statement'].desc()
        ).limit(1)

        slave_call = results_to_dict(slave_result)
        master_call = results_to_dict(master_result)

        master_call_id = master_call[0][row]
        slave_call_id = slave_call[0][row]
        difference = master_call_id - slave_call_id
        # If the difference is 0 -> no work to do
        if not difference:
            return 'success'
        # print(master_call_id, slave_call_id, difference)

        # Don't want to kill the production server
        if difference < 15000:
            query = current_app.config['get_rows_query'].format(
                row_value=row, select_table=table, start_id=slave_call_id, end_id=master_call_id
            )
        else:
            print('Truncating run', table)
            query = current_app.config['get_rows_query'].format(
                row_value=row, select_table=table, start_id=slave_call_id, end_id=slave_call_id + 15000
            )
        print(query)
        master_results = pg_session.execute(
            query
        )

        all_results = results_to_dict(master_results)
        # print(all_results)
    except Exception as e:
        print('bailed', e)
        db_session.rollback()
    else:
        commit_size = len(all_results)
        for result in all_results:
            db_session.add(FETCH[table]['table'](**result))
        db_session.commit()
        return 'Added {} records to {}.'.format(commit_size, table)
    finally:
        db_session.remove()
        pg_session.remove()
        print('still did the finally part')
