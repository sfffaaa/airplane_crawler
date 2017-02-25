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


def GetAirLineResponse(date, origin, destination, proxy):

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


def ProcessAirLineResponse(targetDate, airlineResponse):
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


def _testUsableProxy(raw_proxy):
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
        try:
            logging.warning('Test raw_proxy {0}'.format(raw_proxy))
            s.get('https://booknow.jetstar.com',
                  headers=header,
                  proxies={'https': raw_proxy},
                  timeout=5)
            logging.warning('Test raw_proxy {0} success'.format(raw_proxy))
        except Exception as e:
            logging.debug('Test raw_proxy {0} fail: {1}'.format(raw_proxy, e))
            return False

        return True


def pickUsableProxies(country_raw_proxies):
    """
        >>> pickUsableProxies({"Taiwan": ["104.196.34.46:80", "128.199.229.21:3128"], "Signapore" ["104.196.34.46:80", "128.199.229.21:3128"]}
        ["104.196.34.46:80", "104.196.34.46:80"]
  )
    """
    usable_country_proxies = {}

    for country, raw_proxies in country_raw_proxies.items():
        usable_country_proxies[country] = [_ for _ in raw_proxies if _testUsableProxy(_)]

    for country, proxy in usable_country_proxies.items():
        logging.warning('{0} have {1} proxies'.format(country, len(proxy)))

    return [proxy for _, proxies in usable_country_proxies.items() for proxy in proxies][:8]


def _crawlAirlineData(airplane_data, proxy_data):
    """
        >>> CrawlAirlineData({"updateDate": update_date, "day": 1, "from": "TPE", "to": "DAD"},
                             {"enable": True, "proxies": ["1.1.1.1:80", "2.2.2.2:80"]})
        {'date': '2017/02/21 18:03:44',
         'status': 'ok',
         'data': [{
            'currency': 'TWD',
            'arrival_time':
            '2017/02/21 17:15',
            'air_number': u'BL  163',
            'departure_time': '2017/02/21 15:40',
            'money': 2800.0}
         ]},
        ["1.1.1.1:80"]
    """

    update_date = airplane_data['updateDate']
    from_city = airplane_data['from']
    to_city = airplane_data['to']

    targetDate = update_date + datetime.timedelta(days=airplane_data['day'] + 1)
    logging.warning('targetDate: {0}, origin city: {1}, dest city: {2}'.format(
            targetDate.strftime(PARAM.DATA_ENTRY_DATE_FORMAT), from_city, to_city))

    airlineResponse = ''
    del_proxy_idxs = []
    if not proxy_data['enable']:
        # Without Proxy
        airlineResponse = GetAirLineResponse(targetDate, from_city, to_city, {})
    else:
        # With Proxy
        proxy_list = proxy_data['proxies']
        for idx, proxy in enumerate(proxy_list):
            try:
                logging.warning('Use proxy {0}'.format(proxy))
                airlineResponse = GetAirLineResponse(targetDate, from_city, to_city, {'https': proxy})
                break
            except Exception as e:
                if 'Jet has high loadings, we need try later' in str(e):
                    raise Exception('Jet has high loadings, we need try later')
                else:
                    logging.warning(e)
                    del_proxy_idxs.append(idx)

        # Delete the proxy server which cannot use
        del_proxy_idxs.reverse()

        if 1 >= len(proxy_list) - len(del_proxy_idxs):
            logging.error('Proxy server list remains : {0}'.format(proxy_list))
            raise Exception('Proxy server list remains only {0}'.format(proxy_list))

    if 'Gateway Timeout' in airlineResponse:
        logging.error('Proxy server should change')
        raise Exception('Proxy server should change')
    elif 'Internal Server' in airlineResponse:
        logging.error(airlineResponse)
        raise Exception('Jet has internal error, we need try later')

    return ProcessAirLineResponse(targetDate, airlineResponse), del_proxy_idxs


if __name__ == '__main__':
    update_date = datetime.datetime.now()
    print _crawlAirlineData({"updateDate": update_date, "day": 1, "from": "TPE", "to": "DAD"},
                            {"enable": False, "proxies": []})
