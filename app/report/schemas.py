from marshmallow_sqlalchemy import ModelSchema
from .models import *

"""
Schemas allow serialization/deserialization of ORM Models
"""


class CallSchema(ModelSchema):
    class Meta:
        model = CallTable


class EventSchema(ModelSchema):
    class Meta:
        model = EventTable


class ClientSchema(ModelSchema):
    class Meta:
        model = ClientTable
