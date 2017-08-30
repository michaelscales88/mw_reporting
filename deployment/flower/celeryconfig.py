import os
AMQP_USERNAME = os.getenv('AMQP_USERNAME', 'guest')
AMQP_PASSWORD = os.getenv('AMQP_PASSWORD', 'guest')
AMQP_HOST = os.getenv('AMQP_HOST', 'localhost')
AMQP_PORT = int(os.getenv('AMQP_PORT', '5672'))

DEFAULT_BROKER_URL = [
    'amqp://{}:{}@{}:{}'.format(
        AMQP_USERNAME, AMQP_PASSWORD, host.strip(), AMQP_PORT
    ) for host in AMQP_HOST.split(',') if host.strip()
]

BROKER_URL = os.getenv('BROKER_URL', DEFAULT_BROKER_URL)
RESULT_BACKEND = os.getenv('BACKEND_URL', 'rpc://')

CELERY_ACCEPT_CONTENT = ['myjson']
CELERY_TASK_SERIALIZER = 'myjson'
CELERY_RESULT_SERIALIZER = 'myjson'
