#!/usr/bin/env python
# coding=utf-8

from notifierDB import NotifierDB

EMAIL_LIST = [{
        'from': 'TPE',
        'to': 'OKA',
        'email': 'sfffaaa@gmail.com',
        'money': 1680 - 1
    }, {
        'from': 'OKA',
        'to': 'TPE',
        'email': 'sfffaaa@gmail.com',
        'money': 4780 - 1
    }, {
        'from': 'TPE',
        'to': 'HND',
        'email': 'sfffaaa@gmail.com',
        'money': 2180 - 1
    }, {
        'from': 'HND',
        'to': 'TPE',
        'email': 'sfffaaa@gmail.com',
        'money': 7280 - 1
    }, {
        'from': 'TPE',
        'to': 'KIX',
        'email': 'sfffaaa@gmail.com',
        'money': 1980 - 1
    }, {
        'from': 'KIX',
        'to': 'TPE',
        'email': 'sfffaaa@gmail.com',
        'money': 6980 - 1
    }
]


def isAdminEmailExist(notifier=None):
    if notifier is None:
        notifierDB = NotifierDB()
    else:
        notifierDB == notifier

    listEntries = notifierDB.list({'email': 'sfffaaa@gmail.com'})
    if 0 == len(listEntries):
        return False
    if len(EMAIL_LIST) == len(listEntries):
        return True
    else:
        raise IOError('AdminEmail Exist: {0}, {1}'.format(listEntries, EMAIL_LIST))


def addAdminEmail():
    notifierDB = NotifierDB()
    for _ in EMAIL_LIST:
        listEntries = notifierDB.list({
            'from': _['from'],
            'to': _['to'],
            'email': _['email']
        })
        if 0 != len(listEntries):
            continue
        addIDs = notifierDB.add([_])
        if 0 == addIDs:
            raise IOError('Cannot add entry {0}'.format(_))

    listEntries = notifierDB.list({'email': 'sfffaaa@gmail.com'})
    for _ in listEntries:
        print _


if __name__ == '__main__':
    if not isAdminEmailExist():
        addAdminEmail()
    raise IOError('Souldn\'t call this, Just for initialize')
#    startNotify(nowDate)
