#!/usr/bin/env python
# coding=utf-8

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
import ssl


class ForceTLSV1Adapter(HTTPAdapter):
    """Require TLSv1 for the connection"""
    def init_poolmanager(self, connections, maxsize, block=False):
        # This method gets called when there's no proxy.
        self.poolmanager = PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_version=ssl.PROTOCOL_TLSv1_2,
        )

    def proxy_manager_for(self, proxy, **proxy_kwargs):
        # This method is called when there is a proxy.
        proxy_kwargs['ssl_version'] = ssl.PROTOCOL_TLSv1
        return super(ForceTLSV1Adapter, self).proxy_manager_for(proxy, **proxy_kwargs)
