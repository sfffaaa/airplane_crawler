#!/usr/bin/env python
# coding=utf-8

import os
import base64
import datetime
import sys

try:
    from param import PARAM
except Exception as e:
    sys.path.append(os.getcwd())
    from param import PARAM

import logging

import mailUtils
from email.mime.text import MIMEText

EMAIL_TO_ADDR = 'sfffaaa@gmail.com'

SUCCESS_SUBJECT = 'Jet crawler success at {0}'
SUCCESS_MSG = '''
Jet crawler success at {0}.
You can go to "http://panhome.synology.me:30130/#/jet" to check it.

Here is the successful route.

{1}
'''

FAILURE_SUBJECT = 'Jet crawler failure at {0}'
FAILURE_MSG_LINE = -20
FAILURE_LOG_PATH = 'log/jet.log'
FAILURE_MSG = '''
Jet crawler failure at {0}.

{1}
'''


def sendSuccessMail(date, routeCitys, payPeriods):
    gmail = mailUtils.prepareGMAIL()
    strDate = date.strftime(PARAM.EMAIL_DATE_FORMAT)
    routes = ['    From {0} to {1}: {2} days'.format(cities[0], cities[1], payPeriods) for cities in routeCitys]

    message = MIMEText(SUCCESS_MSG.format(strDate, '\n'.join(routes)))
    message['from'] = PARAM.EMAIL_FROM_ADDR
    message['to'] = EMAIL_TO_ADDR
    message['subject'] = SUCCESS_SUBJECT.format(strDate)

    body = {'raw': base64.urlsafe_b64encode(message.as_string())}
    try:
        gmail.users().messages().send(userId='me', body=body).execute()
        logging.warning('Success: send route email')
    except Exception as e:
        logging.warning('Error: {0}'.format(e))


def sendFailMail(date):
    gmail = mailUtils.prepareGMAIL()
    strDate = date.strftime(PARAM.EMAIL_DATE_FORMAT)
    with open(FAILURE_LOG_PATH) as f:
        lines = f.readlines()
    # Avoid line missing in sent mail...
    lines = [_.replace('WARNING targetDate:', ' - ') for _ in lines[FAILURE_MSG_LINE:]]

    message = MIMEText(FAILURE_MSG.format(strDate, ''.join(lines)))
    message['from'] = PARAM.EMAIL_FROM_ADDR
    message['to'] = EMAIL_TO_ADDR
    message['subject'] = FAILURE_SUBJECT.format(strDate)

    body = {'raw': base64.urlsafe_b64encode(message.as_string())}

    try:
        gmail.users().messages().send(userId='me', body=body).execute()
        logging.warning('Success: send failure email')
    except Exception as e:
        logging.warning('Error: {0}'.format(e))

if __name__ == '__main__':
    import sys
    sys.path.insert(0, '.')
    try:
        from utils import loggingUtils
    except Exception as e:
        print e
        print 'Please execute on project root: {0}'.format(os.getcwd())
        sys.exit(1)

    loggingUtils.setLogSetting(logging.WARNING, 'log/mail.log', '%Y/%m/%d %H:%M:%S')

    TEST_CITY_LIST = [
        ['TPE', 'OKA'],
        ['OKA', 'TPE'],
        ['TPE', 'HND'],
        ['HND', 'TPE'],
        ['TPE', 'KIX'],
        ['KIX', 'TPE']
    ]
    sendSuccessMail(datetime.datetime.now(), TEST_CITY_LIST, 2)
    sendFailMail(datetime.datetime.now())
