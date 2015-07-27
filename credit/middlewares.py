# -*- coding: utf-8 -*-

import os
from scrapy import log
from twisted.internet import defer
from twisted.internet.error import TimeoutError, DNSLookupError, \
        ConnectionRefusedError, ConnectionDone, ConnectError, \
        ConnectionLost, TCPTimedOutError
from scrapy.xlib.tx import ResponseFailed


class UnknownResponseError(Exception):
    """未处理的错误"""
    def __init__(self, value=None):
        self.value = value

    def __str__(self):
        if self.value:
            return repr(self.value)
        else:
            return 'UnknownResponseError'


class Not200Error(Exception):
    """返回不是200的状态码"""
    def __init__(self, value=None):
        self.value = value

    def __str__(self):
        if self.value:
            return repr(self.value)
        else:
            return 'Not200Error'

class RecordWrongPageMiddleware(object):
    # IOError is raised by the HttpCompression middleware when trying to
    # decompress an empty response
    EXCEPTIONS_TO_RETRY = (defer.TimeoutError, TimeoutError, DNSLookupError,
            ConnectionRefusedError, ConnectionDone, ConnectError,
            ConnectionLost, TCPTimedOutError, ResponseFailed,
            IOError, UnknownResponseError)


    def process_spider_exception(self, response, exception, spider):
        if isinstance(exception, self.EXCEPTIONS_TO_RETRY):
            retries = request.meta.get('pageNum', 0)
            log.msg(format="middleware_undown %(request)s %(reason)s",
                    level=log.ERROR, request=request,reason=reason)
            return []



class Not200Middleware(object):
    """处理不是200的情况
    """

    def process_spider_input(self, response, spider):
        if response.status != 200:
            raise Not200Error

    def process_spider_exception(self, response, exception, spider):
        retries = request.meta.get('pageNum', 0)
        log.msg(format="middleware_undown %(request)s %(reason)s",
                level=log.ERROR, request=request,reason=reason)
        return []


