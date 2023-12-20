import logging
import sys

import coloredlogs


def bootstrap():
    logger_name = sys.modules[__name__].__package__.split('.')[0]
    logger = logging.getLogger(logger_name)
    stdout = logging.getLogger('.'.join(['stdout', logger_name]))
    logging.getLogger().addFilter(filter)
    logger_format = '*** %(name)s %(levelname)-7s %(message)s'
    stdout_format = '* %(levelname)-7s %(message)s'
    coloredlogs.install(level='DEBUG', logger=logger, fmt=logger_format)
    coloredlogs.install(level='DEBUG', logger=stdout, fmt=stdout_format)
    logger.setLevel(logging.WARN)
    stdout.setLevel(logging.INFO)
