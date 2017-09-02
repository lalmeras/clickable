from __future__ import print_function  # pylint: disable=unused-import

import logging
import sys

import coloredlogs


def bootstrap():
    logger_name = sys.modules[__name__].__package__.split('.')[0]
    logger = logging.getLogger(logger_name)
    stdout = logging.getLogger('.'.join(['stdout', logger_name]))
    coloredlogs.install(level='WARN', logger=logger)
    coloredlogs.install(level='INFO', logger=stdout)
