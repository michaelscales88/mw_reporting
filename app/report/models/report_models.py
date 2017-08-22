from sqlalchemy import Column, DateTime, Integer, Text
from app.database import Base

from .common import json_type


class ReportCache(Base):
    __searchable__ = []

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    start = Column(DateTime, nullable=False)
    end = Column(DateTime, nullable=False)
    report = Column(json_type)
