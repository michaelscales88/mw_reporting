from sqlalchemy.ext.declarative import DeclarativeMeta
from datetime import datetime
from dateutil import parser
from flask import json
from kombu.serialization import register


CONVERTERS = {
    '__datetime__': parser.parse
}


class AlchemyEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o.__class__, DeclarativeMeta):
            data = {}
            fields = o.__json__() if hasattr(o, '__json__') else dir(o)
            for field in [f for f in fields if not f.startswith('_') and f not in ['metadata', 'query', 'query_class']]:
                value = o.__getattribute__(field)
                try:
                    json.dumps(value)
                    data[field] = value
                except TypeError:
                    data[field] = None
            return data
        if isinstance(o, datetime):
            return {"val": o.isoformat(), "_spec_type": "__datetime__"}
        return json.JSONEncoder.default(self, o)


def object_hook(obj):
    """Convert json data from its serialized value"""
    _spec_type = obj.get('_spec_type')
    if not _spec_type:
        return obj

    if _spec_type in CONVERTERS:
        return CONVERTERS[_spec_type](obj['val'])
    else:
        raise Exception('Unknown {}'.format(_spec_type))


# Encoder function
def my_dumps(obj):
    return json.dumps(obj, cls=AlchemyEncoder)


# Decoder function
def my_loads(obj):
    return json.loads(obj, object_hook=object_hook)


# Set the JSON encoder for Celery
register(
    'myjson',
    my_dumps,
    my_loads,
    content_type='application/x-myjson',
    content_encoding='utf-8'
)