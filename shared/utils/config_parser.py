import os
import sys
from collections import namedtuple
from configparser import RawConfigParser

from shared.utils.exceptions.no_config_file import NoConfigFile

try:
    directory_path = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(directory_path)
except NameError:
    pass


def search_for_file(dirname, filename):

    filepath = os.path.join(dirname, filename)
    if os.path.exists(filepath):
        return filepath
    else:
        filepath = False
        try:
            for name in os.listdir(dirname):
                path = os.path.join(dirname, name)
                if os.path.isdir(path):

                    result = search_for_file(path, filename)

                    filepath = result if result else filepath
        except PermissionError:
            pass

    return filepath


def get_config(app='', filename='proj.conf'):

    config_vars = {}

    for section in ['general', app]:

        filepath = search_for_file(os.path.abspath(''), filename)

        if not filepath:
            raise NoConfigFile

        fp = open(filepath)
        config = RawConfigParser()
        config.read_file(fp)

        if section in config.sections():

            section_vars = dict(config.items(section))

            for section_var, value in section_vars.items():

                try:
                    value = float(value)
                except ValueError:
                    pass

                config_vars[section_var] = value

    config_vars = namedtuple('CONFIG_VARS', config_vars.keys())(*config_vars.values())

    return config_vars
