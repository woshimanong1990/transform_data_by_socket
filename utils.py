# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function
import logging
from logging.handlers import RotatingFileHandler


def setup_logging_and_return_logger(file_name):
    log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d)[%(threadName)s]--- %(message)s')

    my_handler = RotatingFileHandler(file_name, mode='a', maxBytes=5 * 1024 * 1024,
                                     backupCount=5, encoding=None, delay=0)
    my_handler.setFormatter(log_formatter)
    my_handler.setLevel(logging.WARN)

    app_log = logging.getLogger('root')
    app_log.setLevel(logging.WARN)

    app_log.addHandler(my_handler)
    return app_log
