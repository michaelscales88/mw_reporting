import types
from migrate.versioning import api


def migrate():
    v = api.db_version(
        app.config['SQLALCHEMY_DATABASE_URI'],
        app.config['SQLALCHEMY_MIGRATE_REPO']
    )
    migration = app.config['SQLALCHEMY_MIGRATE_REPO'] + ('/versions/%03d_migration.py' % (v + 1))
    tmp_module = types.ModuleType('old_model')
    old_model = api.create_model(
        app.config['SQLALCHEMY_DATABASE_URI'],
        app.config['SQLALCHEMY_MIGRATE_REPO']
    )
    exec(old_model, tmp_module.__dict__)
    script = api.make_update_script_for_model(app.config['SQLALCHEMY_DATABASE_URI'],
                                              app.config['SQLALCHEMY_MIGRATE_REPO'], tmp_module.meta, Base.metadata)
    open(migration, "wt").write(script)
    api.upgrade(
        app.config['SQLALCHEMY_DATABASE_URI'],
        app.config['SQLALCHEMY_MIGRATE_REPO']
    )
    v = api.db_version(
        app.config['SQLALCHEMY_DATABASE_URI'],
        app.config['SQLALCHEMY_MIGRATE_REPO']
    )
    print('New migration saved as ' + migration)
    print('Current database version: ' + str(v))

if __name__ == '__main__':
    import sys
    from os import path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

    from app.database import Base
    from app import app

    migrate()
