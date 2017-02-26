#!/usr/bin/env python
# coding=utf-8

import os
import sys
try:
    from param import PARAM
except Exception as e:
    sys.path.append(os.getcwd())
    from param import PARAM


class CrawlerInfo:
    # update_date is need change name?
    def __init__(self, from_city, to_city, update_date):
        self.from_city = from_city
        self.to_city = to_city
        self.update_date = update_date

    def __str__(self):
        return 'update date: {0}, from {1} to {2}'.format(self.update_date.strftime(PARAM.UPDATE_DATE_FORMAT),
                                                          self.from_city,
                                                          self.to_city)


class AircompanyInfo:
    def __init__(self, name, param, module):
        self.name = name
        self.param = param
        self.module = module
        if not callable(self.module.GetAirLineResponse):
            raise IOError('GetAirLineResponse fail')
        if not callable(self.module.ProcessAirLineResponse):
            raise IOError('ProcessAirLineResponse fail')
