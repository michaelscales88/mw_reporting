from os import urandom, path, environ


class Config(object):
    SECRET_KEY = urandom(24)     # Generate a random session key

    BASEDIR = path.abspath(path.dirname(__file__))
    PACKAGEDIR = path.dirname(BASEDIR)
    PACKAGE_NAME = path.basename(PACKAGEDIR)

    # Default frame settings
    ROWS_PER_PAGE = 50

    # Point to application's database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + path.join(PACKAGEDIR, 'database', 'app.db')
    SQLALCHEMY_MIGRATE_REPO = path.join(PACKAGEDIR, 'database', 'db_repository')
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Keep this off to reduce overhead

    # Configure task Broker/Worker
    # CELERY_BROKER_URL = 'amqp://user:password@rabbit:5672/'
    CELERY_BROKER_URL = 'amqp://user:password@localhost:5672/'
    CELERY_RESULT_BACKEND = 'rpc://'

    # Tell celery to use your json serializer
    CELERY_ACCEPT_CONTENT = ['myjson']
    CELERY_TASK_SERIALIZER = 'myjson'
    CELERY_RESULT_SERIALIZER = 'myjson'

    # email server
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = environ.get('MAIL_PASSWORD')

    # administrator list
    ADMINS = ['your-gmail-username@gmail.com']

    THREAD_LIMIT = 8


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = True  # Turn this off to reduce overhead
