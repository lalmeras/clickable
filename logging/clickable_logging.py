"""Clickable logging framework"""
from __future__ import print_function  # pylint: disable=unused-import

__version__ = "0.9.0"

import logging
import sys

import coloredlogs


_LOG_LEVELS = [
    'critical',
    'debug',
    'error',
    'info',
    'notice',
    'spam',
    'success',
    'verbose',
    'warning'
]

def bootstrap(name, output_name=None,
              stdout_use_name=False, stderr_use_name=True):
    """
    bootstrap a colored logs configuration
    """
    # TODO: load global configuration for verbosity
    if name is None:
        logger_name = "ROOT"
    else:
        logger_name = name
    if output_name is None:
        output_name = logger_name
    log = logging.getLogger("%s.%s" % ('log', logger_name))
    stdout = logging.getLogger("%s.%s" % ('stdout', logger_name))
    stderr = logging.getLogger("%s.%s" % ('stderr', logger_name))

    log_format = '*** %(levelname)-7s %(name)s: %(message)s'

    if stdout_use_name:
        stdout_format = output_name + ' %(message)s'
    else:
        stdout_format = '%(message)s'

    if stderr_use_name:
        stderr_format = '* %(levelname)-7s ' + output_name + ': %(message)s'
    else:
        stderr_format = '%(message)s'

    all_neutral_styles = dict([[level, {}] for level in _LOG_LEVELS])
    coloredlogs.install(level='DEBUG', logger=log, fmt=log_format,
                        stream=sys.stderr)
    # use neutral style for all levels
    coloredlogs.install(level='DEBUG', logger=stdout, fmt=stdout_format,
                        stream=sys.stdout, level_styles=all_neutral_styles)
    coloredlogs.install(level='DEBUG', logger=stderr, fmt=stderr_format,
                        stream=sys.stderr)
    log.setLevel(logging.WARN)
    stdout.setLevel(logging.INFO)
    stderr.setLevel(logging.INFO)
    return Logger(name, output_name, stdout, stderr, log)

class Logger(object):

    _attrs = ['name', 'output_name', 'stdout', 'stderr', 'log']

    def __init__(self,
                 name, output_name,
                 stdout, stderr, log):
        """
        Base logger name (technical)
        """
        self.name = name
        """
        Name used for text output
        """
        self.output_name = output_name
        """
        logger to output on stdout
        """
        self.stdout = stdout
        """
        logger to output on stderr
        """
        self.stderr = stderr
        """
        logger for debugging
        """
        self.log = log

    def __repr__(self):
        return repr(dict([i, getattr(self, i)] for i in Logger._attrs))
