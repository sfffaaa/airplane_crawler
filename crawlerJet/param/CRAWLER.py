#!/usr/bin/env python
# coding=utf-8

from param import JET
from crawler import crawlerJet
from crawler.crawlerClass import AircompanyInfo

# crawler_module:
#   GetAirLineResponse(date, origin, destination, proxy):
#   ProcessAirLineResponse(targetDate, airlineResponse):

TARGET_CRAWLER_INFO = [
    AircompanyInfo('jet', JET, crawlerJet)
]
