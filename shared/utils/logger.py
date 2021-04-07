import logging
import sys


def configure_logger(libraries_level=None):
    logger = logging.getLogger()

    if not isinstance(libraries_level, list):
        libraries_level = []

    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    logger.setLevel(logging.INFO)

    for library, level in libraries_level:
        logging.getLogger(library).setLevel(getattr(logging, level))

    log_handler = logging.StreamHandler(sys.stdout)
    logger.addHandler(log_handler)

    return logger
