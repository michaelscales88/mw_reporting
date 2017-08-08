from sqlalchemy import Column, Text, DateTime, Integer, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship, backref
from sqlalchemy_utils import generic_repr
from app.database import Base


@generic_repr
class CallTable(Base):
    __searchable__ = []

    """
    Parent table
    """
    call_id = Column(Integer, primary_key=True)
    call_direction = Column(Integer)
    calling_party_number = Column(Text)
    dialed_party_number = Column(Text)
    account_code = Column(Text)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    system_id = Column(Integer)
    caller_id = Column(Text)
    inbound_route = Column(Text)

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    @staticmethod
    def src_statement(request_date):
        """Get src rows by running select * from table_name"""
        return """SELECT * FROM c_call WHERE to_char(c_call.start_time, 'YYYY-MM-DD') = '{date}'""".format(
            date=request_date
        )

    def __lt__(self, other):
        # Gives CallTable a sortable property
        return self.call_id < other.call_id


@generic_repr
class EventTable(Base):
    __searchable__ = []

    """
    Child table
    """
    event_id = Column(Integer, primary_key=True)
    event_type = Column(Integer, nullable=False)
    calling_party = Column(Text)
    receiving_party = Column(Text)
    hunt_group = Column(Text)
    is_conference = Column(Text)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    tag = Column(Text)
    recording_rule = Column(Integer)
    call_id = Column(Integer, ForeignKey(CallTable.call_id))

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    @staticmethod
    def src_statement(request_date):
        """Get src rows by running select * from table_name"""
        return """SELECT * FROM c_event WHERE to_char(c_event.start_time, 'YYYY-MM-DD') = '{date}'""".format(
            date=request_date
        )


@generic_repr
class ClientTable(Base):

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, unique=True, nullable=False)
    client_name = Column(Integer, unique=True, nullable=False)
    full_service = Column(Boolean, default=False)

    users = relationship(
        'User',
        secondary='manager_client_link'
    )

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


class ManagerClientLink(Base):
    __tablename__ = 'manager_client_link'
    manager_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    client_id = Column(Integer, ForeignKey('clienttable.client_id'), primary_key=True)
    client = relationship(ClientTable, backref=backref("clienttable_assoc"))
    user = relationship('User', backref=backref("user_assoc"))
