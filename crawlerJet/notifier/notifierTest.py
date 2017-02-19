#!/usr/bin/env python
#coding=utf-8

import unittest
from notifierDB import *

ADD_ENTRIES = [{
	u'from': 'aaa',
	u'to': 'bbb',
	u'email': 'ccccc',
	u'money': 11111,
}, {
	u'from': 'ddd',
	u'to': 'eee',
	u'email': 'fffff',
	u'money': 22222,
}]

EDIT_ENTRIES = [{
	u'from': 'ggg',
	u'to': 'hhh',
	u'email': 'iiiii',
	u'money': 33333,
}, {
	u'from': 'jjj',
	u'to': 'kkk',
	u'email': 'lllll',
	u'money': 44444,
}]

class NotifierDBTest(unittest.TestCase):
	def setUp(self):
		self.assertEquals(1, APP_TEST)
		self.assertEquals(len(EDIT_ENTRIES), len(ADD_ENTRIES))

		tester = NotifierDB()
		ids = tester.list({}, {'_id': 1})
		tester.delete([_['_id'] for _ in ids])

	def testCase1(self):
		tester = NotifierDB()
		result = tester.list()
		self.assertEquals({}, {});

		#Add data
		addIDs = tester.add(ADD_ENTRIES)
		self.assertEquals(len(ADD_ENTRIES), len(addIDs))

		#check added #1
		for _ in addIDs:
			result = tester.list(_)
			#check whether result should in ADD_ENTRIES!
			self.assertEquals(len(result), 1)
			self.assertEquals(result[0] in ADD_ENTRIES, True)

		#check added #2
		result = tester.list()
		self.assertEquals(len(result), len(ADD_ENTRIES))
		for _ in result:
			self.assertEquals(_ in ADD_ENTRIES, True)

		nowIDs = [_['_id'] for _ in ADD_ENTRIES]

		#Edit
		editData = [{'_id': _id, 'data': entry} for _id, entry in zip(nowIDs, EDIT_ENTRIES)]
		editIds = tester.edit(editData)
		self.assertEquals(len(editIds), len(editData))
		for _ in editIds:
			self.assertEquals(_ in nowIDs, True)

		#Check edit
		editData = []
		for _id, entry in zip(nowIDs, EDIT_ENTRIES):
			data = {}
			data['_id'] = _id
			data.update(entry)
			editData.append(data)

		result = tester.list()
		self.assertEquals(len(result), len(editData))
		for _ in result:
			self.assertEquals(_ in editData, True)

		#Delete data
		delIDs = tester.list({}, {'_id': 1})
		self.assertEquals(tester.delete([_['_id'] for _ in delIDs]), True)

		#Check delete data
		delIDs = tester.list({}, {'_id': 1})
		self.assertEquals(len(delIDs), 0)
		

	def tearDown(self):
		tester = NotifierDB()
		ids = tester.list({}, {'_id': 1})
		tester.delete([_['_id'] for _ in ids])

if __name__ == '__main__':
	suite = unittest.TestSuite()
	suite.addTest(NotifierDBTest('testCase1'))
	unittest.TextTestRunner(verbosity=2).run(suite)
