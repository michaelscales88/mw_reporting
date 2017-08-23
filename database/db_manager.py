from os import path
import types
from migrate.versioning import api
from werkzeug.utils import import_string


class DbManager(object):
    def __init__(self):
        self._config_source = None
        self._d = {}
        self._b = None

    @property
    def base(self):
        return self._b

    @base.setter
    def base(self, value):
        self._b = value

    @property
    def config(self):
        return self._d

    def config_from_object(self, obj):
        """Updates the values from the given object.  An object can be of one
        of the following two types:

        -   a string: in this case the object with that name will be imported
        -   an actual object reference: that object is used directly

        Objects are usually either modules or classes. :meth:`from_object`
        loads only the uppercase attributes of the module/class. A ``dict``
        object will not work with :meth:`from_object` because the keys of a
        ``dict`` are not attributes of the ``dict`` class.

        Example of module-based configuration::

            self.config.from_object('yourselflication.default_config')
            from yourselflication import default_config
            self.config.from_object(default_config)

        You should not use this function to load the actual configuration but
        rather configuration defaults.  The actual config should be loaded
        with :meth:`from_pyfile` and ideally from a location not within the
        package because the package might be installed system wide.

        See :ref:`config-dev-prod` for an example of class-based configuration
        using :meth:`from_object`.

        :param obj: an import name or object
        """
        if isinstance(obj, str):
            obj = import_string(obj)
        for key in dir(obj):
            if key.isupper():
                self._d[key] = getattr(obj, key)

    def create(self):
        if not path.exists(self.config['SQLALCHEMY_MIGRATE_REPO']):
            api.create(self.config['SQLALCHEMY_MIGRATE_REPO'], 'database repository')
            api.version_control(
                self.config['SQLALCHEMY_DATABASE_URI'],
                self.config['SQLALCHEMY_MIGRATE_REPO']
            )
        else:
            api.version_control(
                self.config['SQLALCHEMY_DATABASE_URI'],
                self.config['SQLALCHEMY_MIGRATE_REPO'],
                api.version(self.config['SQLALCHEMY_MIGRATE_REPO'])
            )

    def upgrade(self):
        api.upgrade(
            self.config['SQLALCHEMY_DATABASE_URI'],
            self.config['SQLALCHEMY_MIGRATE_REPO']
        )
        v = api.db_version(
            self.config['SQLALCHEMY_DATABASE_URI'],
            self.config['SQLALCHEMY_MIGRATE_REPO']
        )
        print('Current database version: ' + str(v))

    def downgrade(self):
        """
        This script will downgrade the database one revision. 
        You can run it multiple times to downgrade several revisions.
        """
        v = api.db_version(
            self.config['SQLALCHEMY_DATABASE_URI'],
            self.config['SQLALCHEMY_MIGRATE_REPO']
        )
        api.downgrade(
            self.config['SQLALCHEMY_DATABASE_URI'],
            self.config['SQLALCHEMY_MIGRATE_REPO'],
            v - 1
        )
        v = api.db_version(
            self.config['SQLALCHEMY_DATABASE_URI'],
            self.config['SQLALCHEMY_MIGRATE_REPO']
        )
        print('Current database version: ' + str(v))

    def migrate(self):
        if self.base:
            v = api.db_version(
                self.config['SQLALCHEMY_DATABASE_URI'],
                self.config['SQLALCHEMY_MIGRATE_REPO']
            )
            migration = self.config['SQLALCHEMY_MIGRATE_REPO'] + ('/versions/%03d_migration.py' % (v + 1))
            tmp_module = types.ModuleType('old_model')
            old_model = api.create_model(
                self.config['SQLALCHEMY_DATABASE_URI'],
                self.config['SQLALCHEMY_MIGRATE_REPO']
            )
            exec(old_model, tmp_module.__dict__)
            script = api.make_update_script_for_model(
                self.config['SQLALCHEMY_DATABASE_URI'],
                self.config['SQLALCHEMY_MIGRATE_REPO'],
                tmp_module.meta,
                self.base.metadata
            )
            open(migration, "wt").write(script)
            api.upgrade(
                self.config['SQLALCHEMY_DATABASE_URI'],
                self.config['SQLALCHEMY_MIGRATE_REPO']
            )
            v = api.db_version(
                self.config['SQLALCHEMY_DATABASE_URI'],
                self.config['SQLALCHEMY_MIGRATE_REPO']
            )
            print('New migration saved as ' + migration)
            print('Current database version: ' + str(v))
        else:
            print('DbManager Base is not set.')
