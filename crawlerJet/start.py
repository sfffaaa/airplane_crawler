#!/usr/bin/env python
# coding=utf-8

import sys
import logging
import datetime
from param import PARAM, JET
from crawler import crawlerJet
from utils import loggingUtils
from mail import crawlerMail
from mail import notifierMail
from crawler.crawlerDB import CrawlerDB
from crawler import crawlerNoProxy, crawlerProxy
from notifier.notifierDB import NotifierDB


def _startCrawl(update_date, aircompany_data_list, proxy_enable=True):
    for aircompany_dict in aircompany_data_list:
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
                if proxy_enable:
                    airline_data = crawlerProxy.CrawlCityAirlineData({
                                    'updateDate': update_date,
                                    'from': from_city,
                                    'to': to_city
                                  }, aircompany_dict)
                else:
                    airline_data = crawlerNoProxy.CrawlCityAirlineData({
                                    'updateDate': update_date,
                                    'from': from_city,
                                    'to': to_city
                                  }, aircompany_dict)
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


def _startNotifier(update_date, aircompany_data_list):
    for aircompany_dict in aircompany_data_list:
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


def runCrawl(aircompany_data_list, proxy_enable=True):
    try:
        update_date = datetime.datetime.now()
        _startCrawl(update_date, aircompany_data_list, proxy_enable)
    except Exception as e:
        crawlerMail.sendFailMail(update_date)
        logging.warning('Force exit because excption occur {0}'.format(e))
        sys.exit(1)
    else:
        # convert [[['TPE', 'SIN'], ...], [['TPE', 'KIX'], ...]] to [['TPE', 'SIN'], ..] and unique
        city_list = [_['param_module'].CRAWLER_CITY_LIST for _ in aircompany_data_list]
        city_list = [tuple(city) for citys in city_list for city in citys]
        city_list = list(set(city_list))
        city_list = [list(_) for _ in city_list]

        crawlerMail.sendSuccessMail(update_date, city_list, PARAM.DAYS_PERIOD)

    _startNotifier(update_date, aircompany_data_list)

if __name__ == '__main__':
    loggingUtils.setLogSetting(PARAM.LOGGING_LEVEL, PARAM.LOGGING_PATH, PARAM.UPDATE_DATE_FORMAT)

    logging.warning('------------ start --------------')
    runCrawl([{
        'param_module': JET,
        'crawler_module': crawlerJet
    }])
    logging.warning('------------ end --------------')
