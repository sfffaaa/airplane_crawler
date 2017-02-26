#!/usr/bin/env python
# coding=utf-8

import os
import sys
import datetime
import time
try:
    from param import PARAM
except Exception as e:
    sys.path.append(os.getcwd())
    from param import PARAM
import logging
from utils import proxyUtils
from crawler.crawlerClass import CrawlerInfo


class ProxyTestInfo():
    def __init__(self, cache_filename, get_all_proxy=False):
        proxy_list = []

        if cache_filename:
            proxy_list = proxyUtils.GetHighProbabilityProxyList(cache_filename)
        if not proxy_list or get_all_proxy:
            for proxy in proxyUtils.GetAllProxyList():
                if proxy not in proxy_list:
                    proxy_list.append(proxy)

        self.cache_filename = cache_filename
        self.full_proxy_set = set(proxy_list)
        self.not_tested_proxy_set = set(proxy_list)
        self.success_proxy_set = set()
        self.failure_proxy_set = set()
        self.interested_proxy_list = [_ for _ in proxy_list]

    def _refreshInterestedList(self):
        self.interested_proxy_list = [_ for _ in self.interested_proxy_list if _ not in self.failure_proxy_set]

        if 1 >= len(self.interested_proxy_list):
            raise IOError('proxy server list is not enough now')

        self.interested_proxy_list.append(self.interested_proxy_list[0])
        del self.interested_proxy_list[0]

    def AddSuccessProxy(self, proxy):
        self.success_proxy_set.add(proxy)
        self.failure_proxy_set.discard(proxy)
        self.not_tested_proxy_set.discard(proxy)

    def AddFailureProxy(self, proxy):
        self.failure_proxy_set.add(proxy)
        self.success_proxy_set.discard(proxy)
        self.not_tested_proxy_set.discard(proxy)

    def Refresh(self):
        self._refreshInterestedList()

    def IsProxyEnough(self):
        if 1 >= len(self.not_tested_proxy_set) + len(self.success_proxy_set):
            logging.error('Proxy server list not tested len: {0}, success len: {1}'.format(
                          len(self.not_tested_proxy_set),
                          len(self.success_proxy_set)))
            return False
        else:
            return True

    def UpdateCacheFile(self):
        proxyUtils.UpdateHighProbabilityProxyList({
                'success': list(self.success_proxy_set),
                'failure': list(self.failure_proxy_set),
            }, self.cache_filename)


def CrawlAirlineDataPerDay(aircompany_info, crawler_info, day, proxy_tester):
    """
        >>> CrawlAirlineDataPerDay(AircompanyInfo("jet", param.Jet, crawlerJet),
                                   CrawlerInfo("TPE", "DAD", update_date),
                                   1,
                                   ProxyTestInfo(aircompany_info.param.PROXY_HIGH_NAME))
        {'date': '2017/02/21 18:03:44',
         'status': 'ok',
         'data': [{
            'currency': 'TWD',
            'arrival_time':
            '2017/02/21 17:15',
            'air_number': u'BL  163',
            'departure_time': '2017/02/21 15:40',
            'money': 2800.0}
         ]}
    """

    target_crawler_info = CrawlerInfo(crawler_info.from_city,
                                      crawler_info.to_city,
                                      crawler_info.update_date + datetime.timedelta(days=day + 1))

    proxy_list = [_ for _ in proxy_tester.interested_proxy_list]
    logging.warning('With proxy: {0}'.format(target_crawler_info))

    airlineResponse = ''
    for proxy in proxy_list:
        try:
            logging.warning('Use proxy {0}'.format(proxy))
            airlineResponse = aircompany_info.module.GetAirLineResponse(target_crawler_info,
                                                                        {'https': proxy})
            if 'Gateway Timeout' in airlineResponse:
                logging.error('Proxy server should change')
                raise Exception('Proxy server should change')

            proxy_tester.AddSuccessProxy(proxy)
            break
        except Exception as e:
            logging.warning('GetAirLineResponse fail!!!')
            logging.warning(e)
            if 'Jet has high loadings, we need try later' in str(e):
                raise Exception('Jet has high loadings, we need try later')
            else:
                proxy_tester.AddFailureProxy(proxy)
                if not proxy_tester.IsProxyEnough():
                    raise Exception('Proxy server list not enough')

    if 'Internal Server' in airlineResponse:
        logging.error(airlineResponse)
        raise Exception('Jet has internal error, we need try later')

    return aircompany_info.module.ProcessAirLineResponse(target_crawler_info, airlineResponse)


def CrawlCityAirlineData(aircompany_info, crawler_info):
    """
        CrawlCityAirlineData(AircompanyInfo("jet", param.Jet, crawlerJet),
                             CrawlerInfo("TPE", "DAD", update_date))
        {'to': 'DAD',
         'from': 'TPE',
         'updateDate': '2017/02/19 18:06:19',
         'data': [{'date': '2017/02/20 18:06:19', 'status': 'ok', 'data': []},
                  {'date': '2017/02/21 18:06:19', 'status': 'ok', 'data': [{
                        'currency': 'TWD',
                        'arrival_time':
                        '2017/02/21 17:15',
                        'air_number': u'BL  163',
                        'departure_time': '2017/02/21 15:40',
                        'money': 2800.0
                   }]},
                  {'date': '2017/02/22 18:06:19', 'status': 'ok', 'data': []},
                  {'date': '2017/02/23 18:06:19', 'status': 'ok', 'data': []},
                  {'date': '2017/02/24 18:06:19', 'status': 'ok', 'data': [{
                        'currency': 'TWD',
                        'arrival_time': '2017/02/24 17:15',
                        'air_number': u'BL  163',
                        'departure_time': '2017/02/24 15:40',
                        'money': 9300.0
                  }]}
                 ]
        }
    """

    proxy_tester = ProxyTestInfo(aircompany_info.param.PROXY_HIGH_NAME)

    airline_data = []
    proxy_retry_times = 0
    for day in range(PARAM.DAYS_PERIOD):
        for retry_idx, retry_time in enumerate(PARAM.RETRY_SLEEP_TIMES):
            try:
                time.sleep(retry_time)
                airline_entry = CrawlAirlineDataPerDay(aircompany_info,
                                                       crawler_info,
                                                       day,
                                                       proxy_tester)

                proxy_tester.Refresh()

                break
            except Exception as e:
                logging.warning(e)

                if 'high loadings' in str(e):
                    proxy_tester.UpdateCacheFile()
                    raise Exception('High loadings occurs, we need try later')
                elif retry_time == PARAM.RETRY_SLEEP_TIMES[-1]:
                    proxy_tester.UpdateCacheFile()
                    logging.warning('Retry times({0}) is too many times, stop it!'.format(retry_idx))
                    raise Exception('Retry too many times')
                elif 'Proxy server list' in str(e):
                    proxy_tester.UpdateCacheFile()
                    if PARAM.PROXY_RETRY_TIMES < proxy_retry_times:
                        raise IOError('Proxy server retry times({0}) too much times, stop it!'
                                      .format(proxy_retry_times))
                    logging.warning('We need find proxy service again')
                    proxy_retry_times = proxy_retry_times + 1
                    proxy_tester = ProxyTestInfo(aircompany_info.param.PROXY_HIGH_NAME,
                                                 get_all_proxy=True)
                else:
                    logging.warning('We have exception now, {0}. Here is retry times {1}'.format(e, retry_idx))

        airline_data.append(airline_entry)

    logging.debug(airline_data)
    proxy_tester.UpdateCacheFile()

    return airline_data
