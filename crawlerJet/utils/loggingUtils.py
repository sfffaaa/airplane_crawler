#!/usr/bin/env python
# coding=utf-8

import sys
import os
try:
    from param import PARAM
except Exception as e:
    sys.path.append(os.getcwd())
    from param import PARAM
import os
import logging
from logging.handlers import RotatingFileHandler


def createLogFolder(path):
    dirname = os.path.dirname(path)
    if '' == dirname:
        return

    if os.path.exists(dirname):
        if os.path.isdir(dirname):
            return
        else:
            raise IOError('Please check path{0} is dir or not'.format(dirname))

    os.makedirs(dirname)


def setLogSetting(loggingLevel, loggingPath, dateFormat):
    formatter = logging.Formatter(
                    '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    dateFormat)

    logger = logging.getLogger('')
    logger.setLevel(loggingLevel)

    createLogFolder(loggingPath)
    handler = RotatingFileHandler(loggingPath, maxBytes=PARAM.LOGGING_SIZE, backupCount=3)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)
