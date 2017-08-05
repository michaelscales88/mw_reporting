from migrate.versioning import api


def create():
    database.init_db()

    if not path.exists(app.config['SQLALCHEMY_MIGRATE_REPO']):
        api.create(app.config['SQLALCHEMY_MIGRATE_REPO'], 'database repository')
        api.version_control(
            app.config['SQLALCHEMY_DATABASE_URI'],
            app.config['SQLALCHEMY_MIGRATE_REPO']
        )
    else:
        api.version_control(
            app.config['SQLALCHEMY_DATABASE_URI'],
            app.config['SQLALCHEMY_MIGRATE_REPO'],
            api.version(app.config['SQLALCHEMY_MIGRATE_REPO'])
        )

if __name__ == '__main__':
    import sys
    from os import path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

    from app import app
    from app import database

    create()
