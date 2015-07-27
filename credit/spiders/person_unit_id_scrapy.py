#-*- coding:utf-8 -*-
"""
从法院官网爬被执行人公布的名单的id号和更新日期
"""
from scrapy.spider import Spider
from scrapy.http import Request,FormRequest
from scrapy import signals
from scrapy import Selector
from scrapy import log
import re
import os
from credit.items import *

class PersonageCreditt(Spider):
    download_delay=1
    name = 'personid'
    handle_httpstatus_all = True
    writeInFile = "personid"
    start_urls = ['http://shixin.court.gov.cn/personMore.do']
    allowed_domains=['shixin.court.gov.cn']
    def __init__(self):
        self.crawler.signals.connect(self.open_file, \
            signal=signals.spider_opened)  #爬虫开启时，打开文件
        self.crawler.signals.connect(self.close_file, \
            signal=signals.spider_closed)  #爬虫关闭时，关闭文件

    def open_file(self):
        os.chdir("/home/dyh/data/credit/personid")
        self.file_handler = open("writeInFile", "a")

    def close_file(self):
        self.file_handler.close()

    def make_requests_from_url(self,url):
        return Request( url, callback=self.gettotal,dont_filter=True )

    def gettotal(self,response):
        sel = Selector(text=response.body)
        try:
            total = sel.xpath(u"//a[contains(text(),'尾页')]/@onclick").extract()[0]
            total = int(re.findall("\d+",total)[0])
            for i in range(1,total+1)[0:100]:
                yield FormRequest(response.url,
                        formdata={'currentPage': str(i)},
                        headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'},
                        callback=self.listpare,dont_filter=True, meta={'pageNum':str(i)})
        except Exception, e:
            log.msg("total error_info=%s, url=%s" %(e, response.url),level=log.ERROR)

    def listpare(self, response):
        sel = Selector(text=response.body)
        datalist =  sel.xpath("//table[@id='Resultlist']/tbody/tr[position()>1]")
        if len(datalist) == 0:
            log.msg("datalist_empty, url=%s,pageNum=%s, response.body=%s" %(response.url,meta['pageNum'],response.body),level=log.ERROR)
        try:
            content = ''
            item = IdItem()
            for da in datalist:
    #            name = da.select('td[2]/a/text()').extract()[0]
    #            causeserial = da.select('td[3]/text()').extract()[0]
                causedate = da.select('td[4]/text()').extract()[0]
                id = da.xpath('./td[6]/a/@id').extract()[0]
                content = content + str(id) + "\001" + causedate + "\n"
            item["content"] = content
            yield item
        except Exception,e:
            log.msg("datalist error_info=%s, url=%s,pageNum=%s" %(e, response.url,meta['pageNum']),level=log.ERROR)
 