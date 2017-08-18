CELERY_IMPORTS = 'app.report.tasks.sla_report'
CELERY_IGNORE_RESULT = False
BROKER_HOST = "127.0.0.1"  # IP address of the server running RabbitMQ and Celery
BROKER_PORT = 5672
BROKER_URL = 'amqp://'
CELERY_RESULT_BACKEND = "amqp"

# from celery.schedules import crontab

# CELERYBEAT_SCHEDULE = {
#     'every-minute': {
#         'task': 'tasks.multiply',
#         'schedule': crontab(minute='*/1'),
#         'args': (1, 2),
#     },
# }
