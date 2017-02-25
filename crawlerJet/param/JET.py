#!/usr/bin/env python
# coding=utf-8

from param import PARAM

# Needed
if PARAM.APP_TEST:
    CRAWLER_CITY_LIST = [
        ['TPE', 'DAD'],
        ['DAD', 'TPE'],
        ['TPE', 'SIN'],
        ['SIN', 'TPE']
    ]
    MONGODB_DATABASE_NAME = 'jet_test'
else:
    CRAWLER_CITY_LIST = [
        ['TPE', 'DAD'],
        ['DAD', 'TPE'],
        ['TPE', 'SIN'],
        ['SIN', 'TPE']
    ]
    MONGODB_DATABASE_NAME = 'jet'

MONGODB_COLLECTION_NAME = 'jet'

# Self
PROXY_HIGH_NAME = 'proxy.jet'
