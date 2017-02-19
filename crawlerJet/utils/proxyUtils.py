#!/usr/bin/env python
# coding=utf-8

import logging
import requests
from bs4 import BeautifulSoup
import json
import os
import sys

try:
    from param import PARAM
except Exception as e:
    sys.path.append(os.getcwd())
    from param import PARAM


PROXY_URL = 'http://gatherproxy.com/proxylist/country/?c='
DEFAULT_WEIGHT_VALUE = 3

COUNTRY_LIST = ['Taiwan',
                'Singapore',
                # 'Hong%20Kong',
                # 'China',
                'United%20States',
                # 'Japan'
                ]


def _GetProxyList(country):
    r = requests.get(PROXY_URL + country)
    soup = BeautifulSoup(r.text, 'html.parser')
    raw_datas = [_.text.strip()
                 for _ in soup.select('script')
                 if 'gp.insertPrx' in _.text.strip()]

    json_datas = [_.replace('gp.insertPrx(', '')
                   .replace(');', '')
                  for _ in raw_datas]

    proxy_list = sorted([json.loads(_) for _ in json_datas],
                        key=lambda x: int(x['PROXY_TIME']))

    proxy_list = ['{0}:{1}'
                  .format(_['PROXY_IP'].strip(), int(_['PROXY_PORT'].strip(), 16))
                  for _ in proxy_list
                  if _['PROXY_STATUS'].upper() == 'OK']

    return proxy_list


def _GetHighProbabilityProxyDict(filename):
    """
        >>> _GetHighProbabilityProxyDict('proxy.jet')
        {"104.196.34.46:80": 3, "128.199.229.21:3128": 2}

    """
    proxy_dict = {}
    try:
        with open(os.path.join(PARAM.PROXY_FOLDER, filename)) as f:
            proxy_dict = json.load(f)
    except Exception as e:
        logging.debug(e)

    return proxy_dict


def GetHighProbabilityProxyList(filename):
    """
        >>> GetHighProbabilityProxyList('proxy.jet')
        ["104.196.34.46:80", "128.199.229.21:3128"]
    """
    proxy_dict = _GetHighProbabilityProxyDict(filename)
    return [_[0] for _ in sorted(proxy_dict.items(), key=lambda x: x[1], reverse=True)]


def _WriteHighProbabilityProxyList(proxy_dict, filename):
    """
        >>> _WriteHighProbabilityProxyList({"104.196.34.46:80": 3, "128.199.229.21:3128": 2}, "proxy.jet")
    """
    try:
        os.mkdir(PARAM.PROXY_FOLDER)
    except Exception as e:
        logging.debug(e)

    try:
        with open(os.path.join(PARAM.PROXY_FOLDER, filename), 'w') as f:
            json.dump(proxy_dict, f)
    except Exception as e:
        logging.debug(e)


def UpdateHighProbabilityProxyList(tested_proxy_dict, filename):
    """
        not_test_proxies must be the subset of proxies
        >>> UpdateHighProbabilityProxyList({
                'success': ["104.196.34.46:80", "128.199.229.21:3128"],
                'failure': ["1.1.1.1:80"],
            } "proxy.jet")
    """

    logging.warning('Update tested proxy dict {0}'.format(tested_proxy_dict))

    proxy_dict = _GetHighProbabilityProxyDict(filename)
    bad_proxies = [_ for _ in tested_proxy_dict['failure'] if _ in proxy_dict.keys()]
    new_proxies = [_ for _ in tested_proxy_dict['success'] if _ not in proxy_dict.keys()]
    good_proxies = [_ for _ in tested_proxy_dict['success'] if _ in proxy_dict.keys()]

    new_proxy_dict = {key: proxy_dict[key] for key in proxy_dict.keys()}
    for key in bad_proxies:
        new_proxy_dict[key] = new_proxy_dict[key] - 1
    for key in good_proxies:
        new_proxy_dict[key] = new_proxy_dict[key] + 1
    for key in new_proxies:
        new_proxy_dict[key] = DEFAULT_WEIGHT_VALUE
    new_proxy_dict = {key: val for key, val in new_proxy_dict.items() if val > 0}

    _WriteHighProbabilityProxyList(new_proxy_dict, filename)


def GetAllProxyList(test_callback=None):
    """
        >>> GetAllProxyList(None)
        {"Taiwan": ["104.196.34.46:80", "128.199.229.21:3128"],
         "Signapore" ["104.196.34.46:80", "128.199.229.21:3128"]}
    """
    country_proxy = {country: _GetProxyList(country) for country in COUNTRY_LIST}
    logging.warning('Total proxy length {0}'.format(country_proxy))
    if test_callback and callable(test_callback):
        return test_callback(country_proxy)
    else:
        return [proxy for key, val in country_proxy.items() for proxy in val]


if __name__ == '__main__':
    # countries = ['Singapore', 'Taiwan', 'Thailand']
    countries = ['Taiwan']
    country_proxy = {country: _GetProxyList(country) for country in countries}
