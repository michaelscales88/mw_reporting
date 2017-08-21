from sqlalchemy.ext.declarative import DeclarativeMeta
from flask import json
from kombu.serialization import register


class AlchemyEncoder(json.JSONEncoder):

    def default(self, o):
        print('inside AlchemyEncoder')
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
        return json.JSONEncoder.default(self, o)


def decoder(obj):
    print('decoder', flush=True)
    print(obj, flush=True)
    return obj


# Encoder function
def my_dumps(obj):
    print('hitting dumps', flush=True)
    print(obj, flush=True)
    return json.dumps(obj, cls=AlchemyEncoder)


# Decoder function
def my_loads(obj):
    print('hitting loads', flush=True)
    print(obj, flush=True)
    return json.loads(obj, object_hook=decoder)


# Set the JSON encoder for Celery
register(
    'myjson',
    my_dumps,
    my_loads,
    content_type='application/x-myjson',
    content_encoding='utf-8'
)