#!/usr/bin/env python
#coding=utf-8

import unittest
import json
from crawlerDB import *

ADD_ENTRY = {
	u'to' : u'TPE',
	u'from' : u'KIX',
	u'updateDate' : u'2016/07/02 13:22:08',
	u'data' : [{
		u'date' : u'2016/07/03 13:22:08',
		u'status' : u'ok',
		u'data' : [{
			u'currency' : u'¥',
			u'arrival_time' : u'2016/07/03 10:30:00',
			u'air_number' : u'MM023',
			u'departure_time' : u'2016/07/03 08:35:00',
			u'money' : 15480
		}, {
			u'currency' : u'¥',
			u'arrival_time' : u'2016/07/03 17:55:00',
			u'air_number' : u'MM027',
			u'departure_time' : u'2016/07/03 16:00:00',
			u'money' : 21280
		}, {
			u'currency' : u'¥',
			u'arrival_time' : u'2016/07/03 20:05:00',
			u'air_number' : u'MM029',
			u'departure_time' : u'2016/07/03 18:10:00',
			u'money' : 23280
		}]
	}, {
		u'date' : u'2016/07/04 13:22:08',
		u'status' : u'ok',
		u'data' : [{
			u'currency' : u'¥',
			u'arrival_time' : u'2016/07/04 10:30:00',
			u'air_number' : u'MM023',
			u'departure_time' : u'2016/07/04 08:35:00',
			u'money' : 11380
		}, {
			u'currency' : u'¥',
			u'arrival_time' : u'2016/07/04 17:55:00',
			u'air_number' : u'MM027',
			u'departure_time' : u'2016/07/04 16:00:00',
			u'money' : 12980
		}, {
			u'currency' : u'¥',
			u'arrival_time' : u'2016/07/04 20:05:00',
			u'air_number' : u'MM029',
			u'departure_time' : u'2016/07/04 18:10:00',
			u'money' : 12980
		}]
	}]
}

class CralwerDBTest(unittest.TestCase):
	def setUp(self):

		self.assertEquals(1, APP_TEST)
		tester = CrawlerDB()
		ids = tester.list({}, {'_id': 1})
		tester.delete([_['_id'] for _ in ids])

	def testCase1(self):
		tester = CrawlerDB()
		result = tester.list({})
		self.assertEquals({}, {});

		#Add data
		addIDs = tester.add(ADD_ENTRY)
		self.assertEquals(1, len(addIDs))

		#check added #1
		for _ in addIDs:
			result = tester.list(_)
			#check whether result should in ADD_ENTRY!
			self.assertEquals(len(result), 1)
			
			for key, value in ADD_ENTRY.iteritems():
				self.assertEquals(ADD_ENTRY[key], result[0][key])

	def tearDown(self):
		tester = CrawlerDB()
		ids = tester.list({}, {'_id': 1})
		tester.delete([_['_id'] for _ in ids])

if __name__ == '__main__':
	import sys
	sys.path.insert(0, '.')
	try:
		from utils import loggingUtils
	except Exception as e:
		print e
		print 'Please execute on project root: {0}'.format(os.getcwd())
		sys.exit(1)

	suite = unittest.TestSuite()
	suite.addTest(CralwerDBTest('testCase1'))
	unittest.TextTestRunner(verbosity=2).run(suite)

