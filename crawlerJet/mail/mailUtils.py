#!/usr/bin/env python
# coding=utf-8

import os
import argparse
from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client import tools
import httplib2
import sys

try:
    from param import PARAM
except Exception as e:
    sys.path.append(os.getcwd())
    from param import PARAM

import logging
from utils import pathUtils

GMAIL_STORAGE_FILENAME = 'gmail.storage'


def prepareGMAIL():
    parser = argparse.ArgumentParser(parents=[tools.argparser])
    flags = parser.parse_args()
    path = pathUtils.GetGlobalConfigFolderPath()
    # Path to the client_secret.json file downloaded from the Developer Console
    client_secret_filepath = os.path.join(path, PARAM.EMAIL_CLIENT_SECRET_FILENAME)

    # Check https://developers.google.com/gmail/api/auth/scopes for all available scopes
    oauth_scope = 'https://www.googleapis.com/auth/gmail.compose'

    # Location of the credentials storage file
    path = pathUtils.GetCrawlerTmpFolderPath()
    try:
        os.mkdir(path)
    except Exception as e:
        logging.debug(e)

    storage = Storage(os.path.join(path, GMAIL_STORAGE_FILENAME))

    # Start the OAuth flow to retrieve credentials
    flow = flow_from_clientsecrets(client_secret_filepath, scope=oauth_scope)
    http = httplib2.Http()

    # Try to retrieve credentials from storage or run the flow to generate them
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        credentials = tools.run_flow(flow, storage, flags, http=http)

    # Authorize the httplib2.Http object with our credentials
    http = credentials.authorize(http)

    # Build the Gmail service from discovery
    gmail_service = build('gmail', 'v1', http=http)
    return gmail_service
