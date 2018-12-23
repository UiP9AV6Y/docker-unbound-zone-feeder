# -*- coding: utf-8 -*-
'''
'''
import re
import logging

def is_domain(value):
    # cheap regex for service discovery SRV records and regular domain names
    return re.match('[a-zA-Z\_][a-zA-Z0-9.\_\-]*', value)

def is_address(value):
    # cheap regex for IPv4 and IPv6
    return re.match('[a-fA-F0-9.\:]+', value)

class Loggable(object):
    def __init__(self, logger=None):
        self._logger = logger

    def enable_logger(self, logger=None):
        """ Enables a logger to send log messages to """
        if logger is None:
            if self._logger is not None:
                # dont replace existing logger
                return
            logger = logging.getLogger(__name__)
        self._logger = logger

    def disable_logger(self):
        self._logger = None

    def _debug(self, fmt, *args):
        self._log(logging.DEBUG, fmt, *args)

    def _info(self, fmt, *args):
        self._log(logging.INFO, fmt, *args)

    def _warning(self, fmt, *args):
        self._log(logging.WARNING, fmt, *args)

    def _error(self, fmt, *args):
        self._log(logging.ERROR, fmt, *args)

    def _log(self, level, fmt, *args):
        if self._logger is not None:
            self._logger.log(level, fmt, *args)
