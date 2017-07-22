#!flask/bin/python
from migrate.versioning import api
from app import app
api.upgrade(
    app.config['SQLALCHEMY_DATABASE_URI'],
    app.config['SQLALCHEMY_MIGRATE_REPO']
)
v = api.db_version(
    app.config['SQLALCHEMY_DATABASE_URI'],
    app.config['SQLALCHEMY_MIGRATE_REPO']
)
print('Current database version: ' + str(v))
