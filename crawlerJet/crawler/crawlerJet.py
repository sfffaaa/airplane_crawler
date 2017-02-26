#!/usr/bin/env python
# coding=utf-8

import logging
import sys
import requests
import datetime
import os
from bs4 import BeautifulSoup

try:
    from param import PARAM
except Exception as e:
    sys.path.append(os.getcwd())
    from param import PARAM

from utils import httpsAdapter

REQUEST_JET_DATE_FORMAT = '%d/%m/%Y'
REQUEST_JET_MARKET_MONTH = '%Y-%m'
REQUEST_JET_MARKET_DAY = '%d'
REQUEST_FLIGHT_CURRENCY = 'TWD'

RAW_TIME_FORMAT = '%H:%M , %a, %b %d, %Y'
STORE_TIME_FORMAT = '%Y/%m/%d %H:%M:%S'


def GetAirLineResponse(crawler_info, proxy={}):
    date = crawler_info.update_date
    origin = crawler_info.from_city
    destination = crawler_info.to_city

    with requests.Session() as s:
        requestURL = 'https://booknow.jetstar.com'
        s.mount(requestURL, httpsAdapter.ForceTLSV1Adapter())
        header = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch, br',
            'Accept-Language': 'zh-TW,zh;q=0.8,en-US;q=0.6,en;q=0.4',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Host': 'booknow.jetstar.com',
            'Pragma': 'no-cache',
            'Upgrade-Insecure-Requests': 1,
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36'
        }
        s.get('https://booknow.jetstar.com',
              headers=header,
              timeout=5,
              proxies=proxy)

        header = {
            'Host': 'booknow.jetstar.com',
            'Connection': 'keep-alive',
            'Content-Length': 1448,
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'Origin': 'http://www.jetstar.com',
            'Upgrade-Insecure-Requests': 1,
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-TW,zh;q=0.8,en-US;q=0.6,en;q=0.4',
        }
        payload = {
            'culture': 'zh-HK',
            # 'PE_TOKEN': '94589085-2859-4190-a6e8-bb63a72c5d06'
        }
        formdata = {
            'undefined': '',
            'search-help': '',
            'search-origin01': '',
            'search-destination01': '',
            'datedepart-01': date.strftime(REQUEST_JET_DATE_FORMAT),
            'datereturn-01': '',
            'adults': 1,
            'children': 0,
            'infants': 0,
            'travel-indicator': 'on',
            'ControlGroupSearchView$AvailabilitySearchInputSearchView$TextBoxMarketOrigin1': origin,
            'ControlGroupSearchView$AvailabilitySearchInputSearchView$TextBoxMarketDestination1': destination,
            'ControlGroupSearchView$AvailabilitySearchInputSearchView$RadioButtonMarketStructure': 'OneWay',
            'ControlGroupSearchView$AvailabilitySearchInputSearchView$DropDownListMarketDay1': date.strftime(REQUEST_JET_MARKET_DAY),
            'ControlGroupSearchView$AvailabilitySearchInputSearchView$DropDownListMarketMonth1': date.strftime(REQUEST_JET_MARKET_MONTH),
            'ControlGroupSearchView$AvailabilitySearchInputSearchView$DropDownListPassengerType_ADT': 1,
            'ControlGroupSearchView$AvailabilitySearchInputSearchView$DropDownListPassengerType_CHD': 0,
            'ControlGroupSearchView$AvailabilitySearchInputSearchView$DropDownListPassengerType_INFANT': 0,
            'ControlGroupSearchView$AvailabilitySearchInputSearchView$DropDownListCurrency': REQUEST_FLIGHT_CURRENCY,
            'culture': 'zh-TW',
            'ControlGroupSearchView$ButtonSubmit': '',
            '__VIEWSTATE': '',
            'ControlGroupSearchView$AvailabilitySearchInputSearchView$DropDownListFareTypes': 'I',
            'sLkmnwXwAsY=': 'sLkmnwXwAsY=',
            'locale': 'zh-TW',
        }
        r = s.post('https://booknow.jetstar.com/Select.aspx',
                   headers=header,
                   data=formdata,
                   params=payload,
                   proxies=proxy,
                   timeout=40)

        return r.text


def ProcessAirLineResponse(crawler_info, airlineResponse):
    targetDate = crawler_info.update_date
    soup = BeautifulSoup(airlineResponse, 'html.parser')

    exists = soup.select('li.active a span')
    if exists and (u'無' == exists[0].text or u'不可用' == exists[0].text):
        return {
            'date': targetDate.strftime(PARAM.DATA_ENTRY_DATE_FORMAT),
            'data': [],
            'status': 'ok'
        }

    trs = soup.select('div.fare-picker')[0].select('tbody')[0].select('tr')[:-2]
    airlineEntries = []

    for tr in trs:
        airline = {}
        flight_data = tr.select('dd.flight')
        # 0 --> from
        from_time = flight_data[0].contents[1].split(' - ')[0]
        airline['departure_time'] = datetime.datetime.strptime(from_time, RAW_TIME_FORMAT).strftime(PARAM.DATA_ENTRY_DATE_FORMAT)
        # 1 --> to
        to_time = flight_data[1].contents[1].split(' - ')[0]
        airline['arrival_time'] = datetime.datetime.strptime(to_time, RAW_TIME_FORMAT).strftime(PARAM.DATA_ENTRY_DATE_FORMAT)
        # 3 --> type
        airline_type = tr.select('span.flight-no')[0].get_text()
        airline['air_number'] = airline_type

        try:
            money = tr.select('div.field')[0].get_text()
            airline['money'] = float(money.replace('$', '').replace(',', ''))
        except Exception as e:
            logging.error(e)
            logging.error('{0} doens\'t have any fares....'.format(airline['departure_time']))
            continue

        airline['currency'] = REQUEST_FLIGHT_CURRENCY
        airlineEntries.append(airline)

    logging.debug(airlineEntries)

    return {
        'date': targetDate.strftime(PARAM.DATA_ENTRY_DATE_FORMAT),
        'data': airlineEntries,
        'status': 'ok'
    }


if __name__ == '__main__':
    update_date = datetime.datetime.now()
    from crawler.crawlerNoProxy import CrawlAirlineDataPerDay
    from crawler.crawlerClass import AircompanyInfo, CrawlerInfo
    from crawler import crawlerJet
    from param import JET
    print CrawlAirlineDataPerDay(AircompanyInfo("jet", JET, crawlerJet),
                                 CrawlerInfo("TPE", "DAD", update_date),
                                 1)
