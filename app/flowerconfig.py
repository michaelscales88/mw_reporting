import os

AMPQ_ADMIN_USERNAME = os.getenv('AMQP_ADMIN_USERNAME', 'user')
AMPQ_ADMIN_PASSWORD = os.getenv('AMQP_ADMIN_PASSWORD', 'password')
AMQP_ADMIN_HOST = os.getenv('AMQP_ADMIN_HOST', 'localhost')
AMQP_ADMIN_PORT = int(os.getenv('AMQP_ADMIN_PORT', '5672'))

USERNAME = os.getenv('USERNAME', 'root')
PASSWORD = os.getenv('PASSWORD', 'changeit')

DEFAULT_BROKER_URL = 'amqp://{user}:{pw}@{host}:{port}'.format(
        user=AMPQ_ADMIN_USERNAME,
        pw=AMPQ_ADMIN_PASSWORD,
        host=AMQP_ADMIN_HOST,
        port=AMQP_ADMIN_PORT
    )

port = int(os.getenv('FLOWER_PORT', '5555'))
max_tasks = int(os.getenv('FLOWER_MAX_TASKS', '3600'))
basic_auth = [os.getenv('FLOWER_BASIC_AUTH', '%s:%s'
                        % (USERNAME, PASSWORD))]
url_prefix = os.getenv('FLOWER_URL_PREFIX', 'flower')
