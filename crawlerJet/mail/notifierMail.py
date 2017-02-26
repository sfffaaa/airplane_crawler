#!/usr/bin/env python
# coding=utf-8

import os
import base64
import sys

try:
    from param import PARAM
except Exception as e:
    sys.path.append(os.getcwd())
    from param import PARAM

import logging

import mailUtils
from email.mime.text import MIMEText

NOTIFIER_SUBJECT = 'Found Cheaper Jet Ticket ({0} -> {1}) on {2}'
NOTIFIER_MSG = '''
You got cheaper than {0}{1} airplane from {2} to {3} jet!!!
You can got to 'http://panhome.synology.me:30130/#/jet' to check it

Detail Data is below:
{4}
'''


def getResourcePath():
    pathArr = list(os.path.split(os.getcwd()))
    if 'mail' == pathArr[-1]:
        pathArr = pathArr[0:-1]
    pathArr.append('etc')
    return os.path.join(*pathArr)


def composeAirplaneStr(airplaneList):
    line = []
    for _ in airplaneList:
        line.append('Money: {0}{1}, {2} -> {3}, air_number: {4}'.format(
            _['currency'],
            _['money'],
            _['departure_time'],
            _['arrival_time'],
            _['air_number']
        ))
    return '\n'.join(line)


def getAirplaneCurrency(airplaneList):
    return airplaneList[0]['currency']


def sendNotifierMail(person, crawler_info, airplaneList):
    gmail = mailUtils.prepareGMAIL()
    date_str = crawler_info.update_date.strftime(PARAM.EMAIL_DATE_FORMAT)

    airplanesStr = composeAirplaneStr(airplaneList)
    airplaneCurrency = getAirplaneCurrency(airplaneList)

    message = MIMEText(NOTIFIER_MSG.format(airplaneCurrency,
                                           person['money'],
                                           crawler_info.from_city,
                                           crawler_info.to_city,
                                           airplanesStr))
    message['from'] = PARAM.EMAIL_FROM_ADDR
    message['to'] = person['email']
    message['subject'] = NOTIFIER_SUBJECT.format(crawler_info.from_city,
                                                 crawler_info.to_city,
                                                 date_str)

    body = {'raw': base64.urlsafe_b64encode(message.as_string())}
    try:
        gmail.users().messages().send(userId='me', body=body).execute()
        logging.warning('Success: send cheaper email ({0} -> {1})'.format(crawler_info.from_city,
                                                                          crawler_info.to_city))
    except Exception as e:
        logging.warning('Error: {0}'.format(e))

if __name__ == '__main__':
    raise IOError('Doesn\' implement')
