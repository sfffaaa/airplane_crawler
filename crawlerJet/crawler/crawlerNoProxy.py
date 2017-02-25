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


def _crawlAirlineDataPerDay(aircompany_dict, airplane_data):
    """
        >>> _crawlAirlineDataPerDay(JetModule,
            {
                "updateDate": update_date,
                "day": 1,
                "from": "TPE",
                "to": "DAD"
            })
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
    update_date = airplane_data['updateDate']
    from_city = airplane_data['from']
    to_city = airplane_data['to']

    targetDate = update_date + datetime.timedelta(days=airplane_data['day'] + 1)
    logging.warning('targetDate: {0}, origin city: {1}, dest city: {2} without proxy'.format(
            targetDate.strftime(PARAM.DATA_ENTRY_DATE_FORMAT), from_city, to_city))

    airlineResponse = aircompany_func.GetAirLineResponse(targetDate, from_city, to_city, {})

    if 'Gateway Timeout' in airlineResponse:
        logging.error('Proxy server should change')
        raise Exception('Proxy server should change')
    elif 'Internal Server' in airlineResponse:
        logging.error(airlineResponse)
        raise Exception('Jet has internal error, we need try later')

    return aircompany_func.ProcessAirLineResponse(targetDate, airlineResponse)


def CrawlCityAirlineData(airplane_data, aircompany_dict):
    """
        CrawlCityAirlineData({"update_date": dateData, "from": "TPE", "to": "DAD"},
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
    update_date = airplane_data['updateDate']
    from_city = airplane_data['from']
    to_city = airplane_data['to']

    aircompany_param = aircompany_dict['param_module']

    airline_data = []
    for day in range(PARAM.DAYS_PERIOD):
        for retry_idx, retry_time in enumerate(PARAM.RETRY_SLEEP_TIMES):
            try:
                time.sleep(retry_time)
                airline_entry = _crawlAirlineDataPerDay(aircompany_dict, {
                    'updateDate': update_date,
                    'day': day,
                    'from': from_city,
                    'to': to_city
                })
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
    return {
        'updateDate': update_date.strftime(PARAM.UPDATE_DATE_FORMAT),
        'from': from_city,
        'to': to_city,
        'data': airline_data
    }
