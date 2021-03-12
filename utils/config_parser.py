import argparse
from configparser import ConfigParser


def _add_sub_parser(parser, defaults):

    parser.set_defaults(**defaults)

    # parser.add_argument("-i", "--osm-file", help="Path to the osm file")


def _get_config_file_parser():
    conf_parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False,
    )
    conf_parser.add_argument(
        "-c",
        "--conf-file",
        help="Specify config file",
        metavar="FILE",
        default="proj.conf",
    )
    args, remaining_argv = conf_parser.parse_known_args()

    default_config = {}

    if remaining_argv or args.conf_file:
        for command in ['default', 'user-defined']:

            config = ConfigParser()
            config.read(args.conf_file)

            if command in config.sections():
                default_config.update(dict(config.items(command)))

    return conf_parser, default_config, remaining_argv


def get_config():
    conf_parser, default_config, remaining_argv = _get_config_file_parser()

    parser = argparse.ArgumentParser(parents=[conf_parser])

    _add_sub_parser(parser, default_config)

    config, unknown = parser.parse_known_args(remaining_argv)
    return config
