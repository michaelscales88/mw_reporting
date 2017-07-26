# app/lib/flask_extended
# Credit: https://gist.github.com/mattupstate/2046115
# minor modifications to accomodate python 3

import os
import yaml
import types
import errno

from flask import Flask as BaseFlask, Config as BaseConfig


class Config(BaseConfig):
    """Updates the values in the config from a Python file.  This function
    behaves as if the file was imported as module with the
    :meth:`from_object` function.

    :param filename: the filename of the config.  This can either be an
                     absolute filename or a filename relative to the
                     root path.
    :param silent: set to ``True`` if you want silent failure for missing
                   files.

    """
    def from_yaml(self, filename, silent=False):
        filename = os.path.join(self.root_path, filename)
        d = types.ModuleType('config')
        d.__file__ = filename
        try:
            with open(filename, mode='rb') as filename:
                d.__dict__.update(yaml.load(filename))
        except IOError as e:
            if silent and e.errno in (errno.ENOENT, errno.EISDIR):
                return False
            e.strerror = 'Unable to load configuration file (%s)' % e.strerror
            raise
        self.from_object(d)
        return True


class Flask(BaseFlask):
    """Extended version of `Flask` that implements custom config class"""

    def make_config(self, instance_relative=False):
        root_path = self.root_path
        if instance_relative:
            root_path = self.instance_path
        return Config(root_path, self.default_config)
