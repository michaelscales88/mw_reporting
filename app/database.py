from sqlalchemy import create_engine, event
from sqlalchemy.orm import scoped_session
from redpanda.orm import sessionmaker

from app import app
from .model import Base

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

# Bind session to the ORM model query method
Base.query = db_session.query_property()


def init_db():

    # Import models to include in the Base

    from app.user import User
    from app.report import EventTable, CallTable, ReportCache

    Base.metadata.create_all(bind=db_engine)


@event.listens_for(pg_engine, 'begin')
def receive_begin(conn):
    conn.execute('SET TRANSACTION READ ONLY')

# Want to create metadata during app initialization after the engine is created
init_db()
