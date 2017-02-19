#!/usr/bin/env python
#coding=utf-8
import logging

APP_TEST = 1
if APP_TEST:
    SKIP_TIME_PERIOD = 1
    DAYS_PERIOD = 5
else:
    SKIP_TIME_PERIOD = 600
    DAYS_PERIOD = 210
#    raise IOError('Shouldn\'t use real db right now')

DATA_ENTRY_DATE_FORMAT = '%Y/%m/%d %H:%M:%S'

UPDATE_DATE_FORMAT = '%Y/%m/%d %H:%M:%S'
MONGODB_INFO_FILENAME = 'etc/mongo.json'
MONGODB_NOTIFIER_NAME = 'notifier'

RETRY_SLEEP_TIMES = [0.5, 1, 2, 4, 8, 16, 32, 64, 128, 128, 128, 128]

LOGGING_LEVEL = logging.WARNING
LOGGING_PATH = 'log/crawler.log'
LOGGING_SIZE = 10*1024*1024

EMAIL_DATE_FORMAT = '%Y/%m/%d %H:%M:%S'
EMAIL_FROM_ADDR = 'wacouyoyoyo@gmail.com'

PROXY_FOLDER = 'proxy'
PROXY_RETRY_TIMES = 3
