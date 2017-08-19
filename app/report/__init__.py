import flask_excel as excel
from kombu.serialization import register
from marshmallow_sqlalchemy import ModelSchema


from . import views as report_view
from .models import CallTable, EventTable
from app import app
from app.database import db_session


# Make excel responses
excel.init_excel(app)


class CallTableSchema(ModelSchema):
    class Meta:
        model = CallTable
        # attach session for deserialization
        sqla_session = db_session


call_table_schema = CallTableSchema()


# Encoder function
def my_dumps(obj):
    return call_table_schema.dump(obj).data


# Decoder function
def my_loads(obj):
    return call_table_schema.load(obj).data


# Set the JSON encoder for Celery
register(
    'myjson',
    my_dumps,
    my_loads,
    content_type='application/x-myjson',
    content_encoding='utf-8'
)