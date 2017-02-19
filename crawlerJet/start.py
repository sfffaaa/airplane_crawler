#!/usr/bin/env python
# coding=utf-8

import sys
import logging
import datetime
from param import PARAM, CRAWLER
from utils import loggingUtils
from mail import crawlerMail
from mail import notifierMail
from crawler.crawlerDB import CrawlerDB
from notifier.notifierDB import NotifierDB
from utils import proxyUtils
import time


def _crawlCityAirlineData(airplane_data, aircompany_dict, proxy_enable=False):
    """
        _crawlCityAirlineData({"update_date": dateData, "from": "TPE", "to": "DAD"},
                              {"param_module": PARAM.JET, "crawler_module": crawlerJet},
                              False)
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
    aircompany_func = aircompany_dict['crawler_module']

    if from_city not in aircompany_param.CITY_LIST:
        logging.error('Error: wrong origin city {0}'.format(from_city))
        return
    if to_city not in aircompany_param.CITY_LIST:
        logging.error('Error: wrong destionation city {0}'.format(to_city))
        return

    if proxy_enable:
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
                airline_entry = aircompany_func.CrawlAirlineData({
                    'updateDate': update_date,
                    'day': day,
                    'from': from_city,
                    'to': to_city
                }, {
                    'enable': proxy_enable,
                    'proxies': processed_proxy_list
                })
                if 0 != len(not_tested_proxy_list):
                    # Because processed_proxy_list[0] is using prox ok
                    removed_proxy_set = set(proxy_list) - set(processed_proxy_list)
                    not_tested_proxy_list = list(set(not_tested_proxy_list) - set(processed_proxy_list[:1]) - removed_proxy_set)
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
    if proxy_enable:
        proxyUtils.UpdateHighProbabilityProxyList({
                'success': list(set(processed_proxy_list) - set(not_tested_proxy_list)),
                'failure': list(set(proxy_list) - set(processed_proxy_list)),
            }, aircompany_param.PROXY_HIGH_NAME)

    return {
        'updateDate': update_date.strftime(PARAM.UPDATE_DATE_FORMAT),
        'from': from_city,
        'to': to_city,
        'data': airline_data
    }


def _startCrawl(update_date, proxy_enable=True):
    for aircompany_dict in CRAWLER.TARGET_CRAWLER_INFO:
        aircompany_param = aircompany_dict['param_module']
        crawlerDBHandler = CrawlerDB(aircompany_param.MONGODB_DATABASE_NAME,
                                     aircompany_param.MONGODB_COLLECTION_NAME)
        for city_pair in aircompany_param.CRAWLER_CITY_LIST:
            from_city = city_pair[0]
            to_city = city_pair[1]

            logging.warning('{0} -> {1} start crawling'.format(from_city, to_city))
            list_data = crawlerDBHandler.list({
                'from': from_city,
                'to': to_city
            }, {
                'updateDate': 1,
                '_id': 0
            })

            if 0 < len(list_data):
                timediff = update_date - datetime.datetime.strptime(list_data[0]['updateDate'],
                                                                    PARAM.UPDATE_DATE_FORMAT)
                if PARAM.SKIP_TIME_PERIOD > timediff.seconds:
                    logging.warning('{0} -> {1} skip because update time: {2} > {3}'.format(
                        from_city, to_city, PARAM.SKIP_TIME_PERIOD, timediff.seconds))
                    continue
            try:
                airline_data = _crawlCityAirlineData({
                                'updateDate': update_date,
                                'from': from_city,
                                'to': to_city
                              }, aircompany_dict, proxy_enable)
            except Exception as e:
                raise e

            crawlerDBHandler.add(airline_data)
            logging.warning('{0} -> {1} finish crawling'.format(from_city, to_city))


# return (True/False, airplane_data)
def _shouldSendNotifierMail(person_data, crawler_data):
    airplane_list = []
    threshold_ticket = person_data['money']
    for day_data in crawler_data['data']:
        for airplane_data in day_data['data']:
            if threshold_ticket >= airplane_data['money']:
                airplane_list.append(airplane_data)

    return (0 != len(airplane_list), airplane_list)


def _startNotifier(update_date):
    for aircompany_dict in CRAWLER.TARGET_CRAWLER_INFO:
        aircompany_param = aircompany_dict['param_module']
        crawlerDBHandler = CrawlerDB(aircompany_param.MONGODB_DATABASE_NAME,
                                     aircompany_param.MONGODB_COLLECTION_NAME)
        notifierDBHandler = NotifierDB(aircompany_param.MONGODB_DATABASE_NAME,
                                       PARAM.MONGODB_NOTIFIER_NAME)
        for city_pair in aircompany_param.CRAWLER_CITY_LIST:
            from_city = city_pair[0]
            to_city = city_pair[1]

            data_list = crawlerDBHandler.list({
                'from': from_city,
                'to': to_city,
                'updateDate': update_date.strftime(PARAM.UPDATE_DATE_FORMAT)
            }, limit=1)

            email_list = notifierDBHandler.list({
                'from': from_city,
                'to': to_city
            })
            for person in email_list:
                should_send, airplane_list = _shouldSendNotifierMail(person, data_list[0])
                if should_send:
                    notifierMail.sendNotifierMail(update_date, person, city_pair, airplane_list)

if __name__ == '__main__':
    loggingUtils.setLogSetting(PARAM.LOGGING_LEVEL, PARAM.LOGGING_PATH, PARAM.UPDATE_DATE_FORMAT)

    logging.warning('------------ start --------------')
    try:
        update_date = datetime.datetime.now()
        _startCrawl(update_date)
    except Exception as e:
        crawlerMail.sendFailMail(update_date)
        logging.warning('Force exit because excption occur {0}'.format(e))
        sys.exit(1)
    else:
        # convert [[['TPE', 'SIN'], ...], [['TPE', 'KIX'], ...]] to [['TPE', 'SIN'], ..] and unique
        city_list = [_['param_module'].CRAWLER_CITY_LIST for _ in CRAWLER.TARGET_CRAWLER_INFO]
        city_list = [tuple(city) for citys in city_list for city in citys]
        city_list = list(set(city_list))
        city_list = [list(_) for _ in city_list]

        crawlerMail.sendSuccessMail(update_date, city_list, PARAM.DAYS_PERIOD)

    _startNotifier(update_date)

    logging.warning('------------ end --------------')
