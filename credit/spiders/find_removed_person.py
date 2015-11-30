#-*- coding:utf-8 -*-
"""
从法院官网爬被执行人公布名单中被取消的个人
"""
from scrapy.spider import Spider
from scrapy.http import Request,FormRequest
from scrapy import Selector
from scrapy.utils.request import request_fingerprint
from scrapy import signals
from scrapy import log
import re
from credit.items import *
import base64
import redis
import time


class PersonageCreditt(Spider):
    download_delay=0.5
    name = 'person_removed'
    handle_httpstatus_all = True
    myRedis = redis.StrictRedis(host='localhost',port=6379) #connected to redis
    writeInFile = "/home/dyh/data/credit/person/person_removed_%s.txt"
    # writeInFile = "E:/DLdata/person_2015_10_27.txt"
    controlFile = "/home/dyh/data/credit/person/person_control_te.txt"
    # controlFile = "E:/DLdata/person_control.txt"
    start_urls = ['http://www.baidu.com']

    def __init__(self):
        self.file_handler = open(self.writeInFile%time.strftime("%Y_%m_%d"), "a")
        self.file_control = open(self.controlFile, "a+")
        self.url_have_seen = "rmoved_person"
        # for line in self.file_control:
        #     fp = self.url_fingerprint(line)
        #     self.myRedis.sadd(self.url_have_seen,fp)     

    def url_fingerprint(self, url):
        req = Request(url.strip())
        fp = request_fingerprint(req)
        return fp 

    def set_crawler(self, crawler):
        super(PersonageCreditt, self).set_crawler(crawler)
        self.bind_signal()

    def bind_signal(self):
        self.crawler.signals.connect(self.flush_redis, \
                signal=signals.spider_closed)

    def flush_redis(self):
        """
        flush redis db
        """
        self.myRedis.delete(self.url_have_seen)

    def make_requests_from_url(self,url):
        return Request( url, callback=self.gettotal,dont_filter=True )

    def gettotal(self,response):
        """
        """
        for i in self.file_control:
            fp = self.url_fingerprint(url)
            isexist = self.myRedis.sadd(self.url_have_seen,fp)
            if isexist:
                #如果redis set ppai_dup_redis没有则插入并返回1，否则
                #返回0
                yield Request(url,callback=self.detail,meta={'url':url})
            else:
                pass            

    def detail(self,response):
        if response.status == 200:
            # item =PersonMore()
            con_dict = {}
            item = simpleItem()
            self.file_control.write(response.url+"\n")
            body = response.body
            djson = eval(body)
            if len(djson) == 0:
                try:
                    cid = response.url.split("=")[-1]
                    item["content"] = cid +"\n"
                    yield item
                except Exception, e:
                    log.msg("url error url=%s, e=%s"%(response.url, e), level=log.ERROR)
            else:
                pass
        else:
            log.msg("undownloaded info url=%s"%response.meta["url"],level=log.ERROR)   #如果请求不成功（状态码不为200）记录下来
