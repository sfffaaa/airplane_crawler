#!/usr/bin/env python
# coding=utf-8

import os


def GetGlobalConfigFolderPath():
    pathArr = list(os.path.split(os.getcwd()))
    if 'mail' == pathArr[-1]:
        pathArr = pathArr[:-2]
    else:
        pathArr = pathArr[:-1]
    pathArr.append('etc')
    return os.path.join(*pathArr)


def GetCrawlerTmpFolderPath():
    pathArr = list(os.path.split(os.getcwd()))
    if 'mail' == pathArr[-1]:
        pathArr = pathArr[:-1]
    pathArr.append('tmp')
    return os.path.join(*pathArr)


if __name__ == '__main__':
    print GetGlobalConfigFolderPath()
    print GetCrawlerTmpFolderPath()
