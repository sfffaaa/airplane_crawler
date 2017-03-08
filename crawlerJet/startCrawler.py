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
from crawler.crawlerClass import CrawlerInfo, AircompanyInfo
from notifier.notifierDB import NotifierDB


def _isNeedCrawlThisTime(crawler_info, crawlerDBHandler):
    list_data = crawlerDBHandler.list(crawler_info, {
        'updateDate': 1,
        '_id': 0
    })
    if 0 < len(list_data):
        timediff = crawler_info.update_date - datetime.datetime.strptime(list_data[0]['updateDate'],
                                                                         PARAM.UPDATE_DATE_FORMAT)
        if PARAM.SKIP_TIME_PERIOD > timediff.seconds:
            logging.warning('{0} -> {1} no need to crawl because update time: {2} > {3}'.format(
                crawler_info.from_city,
                crawler_info.to_city,
                PARAM.SKIP_TIME_PERIOD,
                timediff.seconds))
            return False

    return True


def _startCrawl(update_date, aircompany_data_list, proxy_enable=True):
    for aircompany_info in aircompany_data_list:
        crawlerDBHandler = CrawlerDB(aircompany_info.param.MONGODB_DATABASE_NAME,
                                     aircompany_info.param.MONGODB_COLLECTION_NAME)
        for city_pair in aircompany_info.param.CRAWLER_CITY_LIST:
            crawler_info = CrawlerInfo(city_pair[0], city_pair[1], update_date)

            logging.warning('{0}: start crawling'.format(crawler_info))
            if not _isNeedCrawlThisTime(crawler_info, crawlerDBHandler):
                continue
            try:
                if proxy_enable:
                    airline_data = crawlerProxy.CrawlCityAirlineData(aircompany_info, crawler_info)
                else:
                    airline_data = crawlerNoProxy.CrawlCityAirlineData(aircompany_info, crawler_info)
            except Exception as e:
                raise e

            crawlerDBHandler.add(crawler_info, airline_data)
            logging.warning('{0}: finish crawling'.format(crawler_info))


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
    for aircompany_info in aircompany_data_list:
        crawlerDBHandler = CrawlerDB(aircompany_info.param.MONGODB_DATABASE_NAME,
                                     aircompany_info.param.MONGODB_COLLECTION_NAME)
        notifierDBHandler = NotifierDB(aircompany_info.param.MONGODB_DATABASE_NAME,
                                       PARAM.MONGODB_NOTIFIER_NAME)
        for city_pair in aircompany_info.param.CRAWLER_CITY_LIST:
            crawler_info = CrawlerInfo(city_pair[0], city_pair[1], update_date)

            data_list = crawlerDBHandler.listWithUpdateDate(crawler_info, limit=1)
            email_list = notifierDBHandler.list(crawler_info)

            for person in email_list:
                should_send, airplane_list = _shouldSendNotifierMail(person, data_list[0])
                if should_send:
                    notifierMail.sendNotifierMail(person, crawler_info, airplane_list)


def _runCrawl(aircompany_data_list, proxy_enable=True):
    try:
        update_date = datetime.datetime.now()
        _startCrawl(update_date, aircompany_data_list, proxy_enable)
    except Exception as e:
        crawlerMail.sendFailMail(update_date)
        logging.warning('Force exit because excption occur {0}'.format(e))
        sys.exit(1)
    else:
        # convert [[['TPE', 'SIN'], ...], [['TPE', 'KIX'], ...]] to [['TPE', 'SIN'], ..] and unique
        city_list = [_.param.CRAWLER_CITY_LIST for _ in aircompany_data_list]
        city_list = [tuple(city) for citys in city_list for city in citys]
        city_list = list(set(city_list))
        city_list = [list(_) for _ in city_list]

        crawlerMail.sendSuccessMail(update_date, city_list, PARAM.DAYS_PERIOD)

    _startNotifier(update_date, aircompany_data_list)

if __name__ == '__main__':
    loggingUtils.setLogSetting(PARAM.LOGGING_LEVEL, PARAM.LOGGING_PATH, PARAM.UPDATE_DATE_FORMAT)

    logging.warning('------------ start --------------')
    _runCrawl([AircompanyInfo('jet', JET, crawlerJet)])
    logging.warning('------------ end --------------')
