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
from crawler.crawlerClass import CrawlerInfo


def _crawlAirlineDataPerDay(aircompany_dict, crawler_info, day):
    """
        >>> _crawlAirlineDataPerDay(JetModule, CrawlerInfo("TPE", "DAD", update_date), 1)
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

    aircompany_func = aircompany_dict['crawler_module']
    target_crawler_info = CrawlerInfo(crawler_info.from_city,
                                      crawler_info.to_city,
                                      crawler_info.update_date + datetime.timedelta(days=day + 1))

    logging.warning('Without proxy: {0}'.format(target_crawler_info))

    airlineResponse = aircompany_func.GetAirLineResponse(target_crawler_info)

    if 'Gateway Timeout' in airlineResponse:
        logging.error('Proxy server should change')
        raise Exception('Proxy server should change')
    elif 'Internal Server' in airlineResponse:
        logging.error(airlineResponse)
        raise Exception('Jet has internal error, we need try later')

    return aircompany_func.ProcessAirLineResponse(target_crawler_info, airlineResponse)


def CrawlCityAirlineData(crawler_info, aircompany_dict):
    """
        CrawlCityAirlineData(CrawlerInfo("TPE", "DAD", update_date),
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

    airline_data = []
    for day in range(PARAM.DAYS_PERIOD):
        for retry_idx, retry_time in enumerate(PARAM.RETRY_SLEEP_TIMES):
            try:
                time.sleep(retry_time)
                airline_entry = _crawlAirlineDataPerDay(aircompany_dict, crawler_info, day)
                break
            except Exception as e:
                logging.warning(e)

                if 'high loadings' in str(e):
                    raise Exception('High loadings occurs, we need try later')
                elif retry_time == PARAM.RETRY_SLEEP_TIMES[-1]:
                    logging.warning('Retry times({0}) is too many times, stop it!'.format(retry_idx))
                    raise Exception('Retry too many times')
                else:
                    logging.warning('We have exception now, {0}. Here is retry times {1}'.format(e, retry_idx))

        airline_data.append(airline_entry)

    logging.debug(airline_data)
    return airline_data
