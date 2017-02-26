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


def _crawlAirlineDataPerDay(aircompany_dict, crawler_info, day, proxy_list):
    """
        >>> _crawlAirlineDataPerDay(JetModule,
                                    CrawlerInfo("TPE", "DAD", update_date),
                                    1,
                                    ["1.1.1.1:80", "2.2.2.2:80"])
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

    aircompany_func = aircompany_dict['crawler_module']
    target_crawler_info = CrawlerInfo(crawler_info.from_city,
                                      crawler_info.to_city,
                                      crawler_info.update_date + datetime.timedelta(days=day + 1))

    logging.warning('With proxy: {0}'.format(target_crawler_info))

    airlineResponse = ''
    del_proxy_idxs = []
    for idx, proxy in enumerate(proxy_list):
        try:
            logging.warning('Use proxy {0}'.format(proxy))
            airlineResponse = aircompany_func.GetAirLineResponse(target_crawler_info,
                                                                 {'https': proxy})
            break
        except Exception as e:
            logging.warning('GetAirLineResponse fail!!!')
            logging.warning(e)
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

    return aircompany_func.ProcessAirLineResponse(target_crawler_info, airlineResponse), del_proxy_idxs


def CrawlCityAirlineData(crawler_info, aircompany_dict):
    """
        CrawlCityAirlineData(CrawlerInfo("TPE", "DAD", date_date),
                             {"param_module": PARAM.JET, "crawler_module": crawlerJet})
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

    aircompany_param = aircompany_dict['param_module']

    proxy_list = proxyUtils.GetHighProbabilityProxyList(aircompany_param.PROXY_HIGH_NAME)
    if not proxy_list:
        proxy_list = proxyUtils.GetAllProxyList()

    not_tested_proxy_list = [_ for _ in proxy_list]
    processed_proxy_list = [_ for _ in proxy_list]

    airline_data = []
    proxy_retry_times = 0
    for day in range(PARAM.DAYS_PERIOD):
        for retry_idx, retry_time in enumerate(PARAM.RETRY_SLEEP_TIMES):
            try:
                time.sleep(retry_time)
                airline_entry, del_proxy_idxs = _crawlAirlineDataPerDay(aircompany_dict,
                                                                        crawler_info,
                                                                        day,
                                                                        processed_proxy_list)

                if del_proxy_idxs:
                    for del_idx in del_proxy_idxs:
                        del processed_proxy_list[del_idx]

                if 0 != len(not_tested_proxy_list):
                    # Because processed_proxy_list[0] is using prox ok
                    removed_proxy_set = set(proxy_list) - set(processed_proxy_list)
                    not_tested_proxy_list = list(set(not_tested_proxy_list) - set(processed_proxy_list[:1]) - removed_proxy_set)

                if 0 == len(processed_proxy_list):
                    raise IOError('Proxy server list should reget again')

                # rotate the success proxy one
                processed_proxy_list.append(processed_proxy_list[0])
                del processed_proxy_list[0]
                break
            except Exception as e:
                logging.warning(e)

                if 'high loadings' in str(e):
                    raise Exception('High loadings occurs, we need try later')
                elif retry_time == PARAM.RETRY_SLEEP_TIMES[-1]:
                    logging.warning('Retry times({0}) is too many times, stop it!'.format(retry_idx))
                    raise Exception('Retry too many times')
                elif 'Proxy server list' in str(e):
                    if PARAM.PROXY_RETRY_TIMES < proxy_retry_times:
                        raise
                    logging.warning('We find proxy service again')
                    proxy_retry_times = proxy_retry_times + 1
                    proxy_list = proxyUtils.GetAllProxyList()
                    not_tested_proxy_list = [_ for _ in proxy_list]
                    processed_proxy_list = [_ for _ in proxy_list]
                else:
                    logging.warning('We have exception now, {0}. Here is retry times {1}'.format(e, retry_idx))

        airline_data.append(airline_entry)

    logging.debug(airline_data)
    proxyUtils.UpdateHighProbabilityProxyList({
            'success': list(set(processed_proxy_list) - set(not_tested_proxy_list)),
            'failure': list(set(proxy_list) - set(processed_proxy_list)),
        }, aircompany_param.PROXY_HIGH_NAME)

    return airline_data
