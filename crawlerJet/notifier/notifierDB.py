#!/usr/bin/env python
# coding=utf-8

import sys
import pymongo
import base64
import os
import json

try:
    from param import PARAM
except Exception as e:
    sys.path.append(os.getcwd())
    from param import PARAM, JET

from utils import pathUtils
import logging

ENTRY_MUST_KEYS = ['from', 'to', 'email', 'money']


class NotifierDB:
    def __init__(self, db_name, collection_name):
        path = os.path.join(pathUtils.GetGlobalConfigFolderPath(), PARAM.MONGODB_INFO_FILENAME)
        with open(path) as f:
            mongo_info = json.load(f)

        self.client = pymongo.MongoClient(mongo_info['url'], mongo_info['port'])
        if not self.client[db_name].authenticate(
                mongo_info['username'],
                mongo_info['password']):
            logging.error('mongo db cannot authenticate')
            raise IOError('mongodb cannot authenticate')
        self.collection = self.client[db_name][collection_name]

    def __del__(self):
        self.client.close()

    # return idlist, user should check whether the return size is the same as entryList size
    '''
        [{
            'from': aaa,
            'to': bbb,
            'email': aabbb,
            'money': 10000,
            'sent': none
        }, {
            'from': aaa,
            'to': bbb,
            'email': aabbb,
            'money': 10000,
            'sent': none
        }]
    '''
    def add(self, entryList):
        for entry in entryList:
            for key in ENTRY_MUST_KEYS:
                if key not in entry:
                    logging.error('Wrong parameter: {0} not in kargs {1}'.format(key, entry))
                    return []

        result = self.collection.insert_many(entryList)
        ids = []
        for _ in result.inserted_ids:
            ids.append({u'_id': _})
        return ids

    '''
        [{
            id: ObjectId('54f113fffba522406c9cc20e'),
            data: {
                'from': aaa,
                'to': bbb,
                'email': aabbb,
                'money': 10000,
                'sent': none
            }
        }, {
            ...
        }],
    '''
    def edit(self, entryList):
        successList = []
        for entry in entryList:
            data = self.collection.update({
                '_id': entry['_id']
            }, {
                '$set': entry['data']
            }, upsert=False)

            if 1 == data['ok']:
                successList.append(True)
            else:
                successList.append(False)

        retList = []
        for _ in zip(entryList, successList):
            if _[1]:
                retList.append(_[0]['_id'])
        return retList

    def list(self, filters={}, condition={}, skip=0, limit=0):
        if len(condition):
            cursor = self.collection.find(
                filters,
                condition,
                skip=skip,
                limit=limit,
            ).sort([
                ('money', pymongo.DESCENDING)
            ])
        else:
            cursor = self.collection.find(
                filters,
                skip=skip,
                limit=limit,
            ).sort([
                ('money', pymongo.DESCENDING)
            ])
        return [people for people in cursor]

    '''
        [ObjectId('54f113fffba522406c9cc20e'), ObjectId('54f113fffba522406c9cc20f')]
    '''
    def delete(self, idsList):
        if not isinstance(idsList, list):
            return False
        self.collection.remove({
            '_id': {'$in': idsList}
        })
        return True
