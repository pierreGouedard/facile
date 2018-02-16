"""
Global configuration that may be overridden by user
"""

# Global imports
from __future__ import print_function
import os
import yaml
import copy
import sys
import pkg_resources


DEFAULT_CONF = {
    'facile.drivers': ['file'],
    'facile.data.dir': 'DATA',
    'facile.local.path': '~/.local/facile',
    'facile.driver.file.workspace': '',
    'facile.driver.file.tmpdir': '/tmp',
    'facile.package.list': ['settings'],
}

"""Default settings configuration"""


def _load_from_file(path, filename, absent_ok=False):
    """
    Load from a file

    :param path: absolute path to the directory
    :param filename: relative path from the directory
    :rtype: dict
    """
    # Check whether file exists
    file_path = os.path.join(path, filename)
    if not os.path.exists(file_path):
        if not absent_ok:
            print('[Warning] Could not find setting file {}'.format(file_path), file=sys.stderr)
        return {}

    try:
        with open(file_path) as fd:
            conf = yaml.load(fd)
        if conf is None:  # If the file is empty
            conf = {}
    except ImportError as e:
        print(e, file=sys.stderr)
        conf = {}
    except IOError as e:
        print(e, file=sys.stderr)
        conf = {}

    # Update conf with the imports specified in the current file
    for import_path in conf.get('imports', []):
        conf.update(_load_from_file(path, import_path))

    return conf


def _load_from_package(package, path):
    """
    Load from a python-like package (or a .zip)

    :param package: importable package (like mypackage.submodule)
    :param path: relative path inside the package
    :rtype: dict
    """
    try:
        with pkg_resources.resource_stream(package, path) as fd:
            conf = yaml.load(fd)
        if conf is None:  # If the file is empty
            conf = {}
    except ImportError as e:
        # print(e, file=sys.stderr)
        conf = {}
    except IOError as e:
        # print(e, file=sys.stderr)
        conf = {}

    # Update conf with the imports specified in the current file
    for import_path in conf.get('imports', []):
        conf.update(_load_from_package(package, import_path))

    return conf


class Settings(object):
    def __init__(self):
        self.loaded = False
        self.settings = {}

    def __getitem__(self, item):
        if not self.loaded:
            settings.load()
        return self.settings[item]

    # Useful to set data_pm.running_mode
    def __setitem__(self, key, value):
        if not self.loaded:
            settings.load()
        self.settings[key] = value

    def __contains__(self, item):
        return item in self.settings

    def items(self):
        for k, v in self.settings.items():
            yield k, v

    def get(self, item, default=None):
        if not self.loaded:
            settings.load()
        return self.settings[item] if item in self.settings else default

    def expand(self, item, user='', default=None):
        value = self.get(item)
        if not value:
            return default
        value = value.replace('~', '~{}'.format(user))
        return os.path.expanduser(value)

    def load(self):
        # Copy the default configuration
        self.settings = copy.deepcopy(DEFAULT_CONF)

        # Update conf with user settings
        self.settings.update(_load_from_file(os.path.expanduser(self.settings['data_pm.local.path']),
                                             'settings.yml', absent_ok=True))

        # Update conf with local settings
        self.settings.update(_load_from_file('settings', 'settings.yml', absent_ok=True))
        self.settings.update(_load_from_package('settings', 'settings.yml'))

        self.loaded = True

        return self.settings


settings = Settings()

