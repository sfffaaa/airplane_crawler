#!/usr/bin/env python
# coding=utf-8

import logging
import os
import sys
try:
    from param import PARAM
except Exception as e:
    sys.path.append(os.getcwd())
    from param import PARAM

import pymongo
from pymongo import MongoClient
import json

class CrawlerDB:
    def __init__(self, db_name, collection_name):
        with open(PARAM.MONGODB_INFO_FILENAME) as f:
            mongo_info = json.load(f)
        self.client = MongoClient(mongo_info['url'], mongo_info['port'])
        if not self.client[db_name].authenticate(
                mongo_info['username'],
                mongo_info['password']):
            logging.error('mongo db cannot authenticate')
            raise IOError('mongodb cannot authenticate')
        self.collection = self.client[db_name][collection_name]

    def __del__(self):
        self.client.close()

    def delete(self, idsList):
        if not isinstance(idsList, list):
            return False
        self.collection.remove({
            '_id': {
                '$in': idsList
            }
        })
        return True

    def edit(self, entryList):
        raise IOError('Not implement')

    def list(self, filters={}, condition={}, skip=0, limit=0):
        if len(condition):
            cursor = self.collection.find(
                filters,
                condition,
                skip=skip,
                limit=limit,
            ).sort([
                ('updateDate', pymongo.DESCENDING)
            ])
        else:
            cursor = self.collection.find(
                filters,
                skip=skip,
                limit=limit,
            ).sort([
                ('updateDate', pymongo.DESCENDING)
            ])
        return [data for data in cursor]

    def add(self, data):
        result = self.collection.save(data)
        return [{'_id': result}]
