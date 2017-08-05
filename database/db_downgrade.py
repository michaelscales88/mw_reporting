from migrate.versioning import api


def downgrade():
    """
    This script will downgrade the database one revision. You can run it multiple times to downgrade several revisions.
    """
    v = api.db_version(
        app.config['SQLALCHEMY_DATABASE_URI'],
        app.config['SQLALCHEMY_MIGRATE_REPO']
    )
    api.downgrade(
        app.config['SQLALCHEMY_DATABASE_URI'],
        app.config['SQLALCHEMY_MIGRATE_REPO'],
        v - 1
    )
    v = api.db_version(
        app.config['SQLALCHEMY_DATABASE_URI'],
        app.config['SQLALCHEMY_MIGRATE_REPO']
    )
    print('Current database version: ' + str(v))

if __name__ == '__main__':
    import sys
    from os import path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

    from app import app

    downgrade()
