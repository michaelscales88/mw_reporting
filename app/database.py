from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session
from redpanda.orm import sessionmaker

from app import app

# Internal db
db_engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=db_engine))

# Source db
pg_engine = create_engine(app.config['PG_CONNECTION'])
pg_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=pg_engine))

# MS SQL db
# ms_engine = create_engine(app.config['MSSQL_CONNECTION'])
# ms_session = scoped_session(sessionmaker(autocommit=False,
#                                          autoflush=False,
#                                          bind=ms_engine))

Base = declarative_base()
Base.query = db_session.query_property()


def init_db():

    # Import models to include in the Base

    from app.user import User
    from app.report import EventTable, CallTable

    Base.metadata.create_all(bind=db_engine)


# @event.listens_for(db_session, 'transient_to_pending')
# def object_is_pending(session, obj):
#     print('New pending in {session}: {object}'.format(session=session, object=obj))


# @event.listens_for(ms_engine, 'begin')
@event.listens_for(pg_engine, 'begin')
def receive_begin(conn):
    conn.execute('SET TRANSACTION READ ONLY')
