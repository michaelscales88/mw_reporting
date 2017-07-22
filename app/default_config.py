from os import urandom, path, environ, makedirs


class Config(object):
    WTF_CSRF_ENABLED = True
    SECRET_KEY = urandom(24)     # Generate a random session key

    BASEDIR = path.abspath(path.dirname(__file__))
    PACKAGEDIR = path.dirname(BASEDIR)
    PACKAGE_NAME = path.basename(PACKAGEDIR)

    # Model database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + path.join(BASEDIR, 'app.db')
    SQLALCHEMY_MIGRATE_REPO = path.join(BASEDIR, 'db_repository')
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Turn this off to reduce overhead

    # indexing service
    WHOOSH_BASE = path.join(BASEDIR, 'tmp/whoosh')
    ENABLE_SEARCH = False

    # email server
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = environ.get('MAIL_PASSWORD')

    # administrator list
    ADMINS = ['your-gmail-username@gmail.com']


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = True  # Turn this off to reduce overhead
    EXTERNAL_CONNECTION = 'postgresql://Chronicall:ChR0n1c@ll1337@10.1.3.17:9086/chronicall'

    # Test statement
    TEST_STATEMENT = '''
    Select Distinct c_call.call_id, c_call.dialed_party_number, c_call.calling_party_number, c_event.*
    From c_event
        Inner Join c_call on c_event.call_id = c_call.call_id
    where
        to_char(c_call.start_time, 'YYYY-MM-DD') = '2017-07-05' and
        c_call.call_direction = 1
    Order by c_call.call_id, c_event.event_id
    '''


class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + ':memory:'
    TESTING = True
    DEBUG = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_ECHO = False
