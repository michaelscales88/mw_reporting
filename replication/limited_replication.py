from datetime import datetime


def results_to_dict(ptr):
    col_names = [item[0] for item in ptr._cursor_description()]
    return [dict(zip(col_names, row)) for row in ptr]   # Column: Cell pairs


def replicate_call(current_id):
    print('inside call replicate')
    # q2 = db_session.query(CallTable.call_id).order_by(CallTable.call_id.desc()).first()
    # current_id = q2[0]
    print('fetching records from', current_id)
    print('start pull', datetime.utcnow(), flush=True)
    new_statement = """SELECT * FROM c_call WHERE call_id > {current_id} ORDER BY call_id DESC""".format(
        current_id=current_id
    )
    # print(new_statement)
    q3 = pg_session.execute(new_statement)
    print('stop pull', datetime.utcnow(), flush=True)
    print('start zip', datetime.utcnow(), flush=True)
    zipped_results = results_to_dict(q3)
    print('stop zip', datetime.utcnow(), flush=True)
    print('start model', datetime.utcnow(), flush=True)
    for result in zipped_results:
        model = CallTable(**result)
        db_session.add(model)
    db_session.commit()
    db_session.remove()
    print(len(zipped_results))
    print('stop model', datetime.utcnow(), flush=True)


def replicate_event(current_id):
    print('inside event replicate')
    print('fetching records from', current_id)
    print('start pull', datetime.utcnow(), flush=True)
    new_statement = """
    SELECT * 
    FROM c_event 
    WHERE event_id > {current_id} 
    AND event_id < {other_id} 
    ORDER BY event_id DESC""".format(
        current_id=current_id,
        other_id=current_id+170000
    )
    # print(new_statement)
    q3 = pg_session.execute(new_statement)
    print('stop pull', datetime.utcnow(), flush=True)
    print('start zip', datetime.utcnow(), flush=True)
    zipped_results = results_to_dict(q3)
    print('stop zip', datetime.utcnow(), flush=True)
    print('start model', datetime.utcnow(), flush=True)
    for result in zipped_results:
        model = EventTable(**result)
        db_session.add(model)
    db_session.commit()
    db_session.remove()
    print(len(zipped_results))
    print('stop model', datetime.utcnow(), flush=True)


if __name__ == '__main__':
    import sys
    from os import path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

    from app.database import pg_session, db_session
    from app.report import CallTable, EventTable

    # replicate_call(1400897)
    replicate_event(5732735)



