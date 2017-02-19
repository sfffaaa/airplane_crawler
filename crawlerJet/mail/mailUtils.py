#!/usr/bin/env python
# coding=utf-8

import os
import argparse
from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client import tools
import httplib2


def getResourcePath():
    pathArr = list(os.path.split(os.getcwd()))
    if 'mail' == pathArr[-1]:
        pathArr = pathArr[:-1]
    pathArr.append('etc')
    return os.path.join(*pathArr)


def prepareGMAIL():
    parser = argparse.ArgumentParser(parents=[tools.argparser])
    flags = parser.parse_args()
    path = getResourcePath()
    # Path to the client_secret.json file downloaded from the Developer Console
    CLIENT_SECRET_FILE = os.path.join(path, 'client_secret.json')

    # Check https://developers.google.com/gmail/api/auth/scopes for all available scopes
    OAUTH_SCOPE = 'https://www.googleapis.com/auth/gmail.compose'

    # Location of the credentials storage file
    STORAGE = Storage(os.path.join(path, 'gmail.storage'))

    # Start the OAuth flow to retrieve credentials
    flow = flow_from_clientsecrets(CLIENT_SECRET_FILE, scope=OAUTH_SCOPE)
    http = httplib2.Http()

    # Try to retrieve credentials from storage or run the flow to generate them
    credentials = STORAGE.get()
    if credentials is None or credentials.invalid:
        credentials = tools.run_flow(flow, STORAGE, flags, http=http)

    # Authorize the httplib2.Http object with our credentials
    http = credentials.authorize(http)

    # Build the Gmail service from discovery
    gmail_service = build('gmail', 'v1', http=http)
    return gmail_service
