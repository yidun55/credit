#-*- coding:utf-8 -*-
"""
从法院官网爬被执行人公布的名单
"""
from scrapy.spider import Spider
from scrapy.http import Request,FormRequest
from scrapy import signals
from scrapy import log
import re
from credit.items import *

class PersonageCreditt(Spider):
    #download_delay=30
    name = 'person'
    handle_httpstatus_all = True
    writeInFile = "personMore"
    start_urls = ['http://shixin.court.gov.cn/personMore.do']
    allowed_domains=['shixin.court.gov.cn']
    def __init__(self):
        pass

    def make_requests_from_url(self,url):
        return Request( url, callback=self.gettotal,dont_filter=True )

    def gettotal(self,response):
        hxs = response.selector
        try:
            total = hxs.xpath(u"//a[contains(text(),'尾页')]/@onclick").extract()[0]
            total = int(re.findall("\d+",total)[0])
            for i in range(1,total+1):
                yield FormRequest(response.url,
                        formdata={'currentPage': str(i)},
                        headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'},
                        callback=self.listpare,dont_filter=True, meta={'pageNum':str(i)})
        except Exception, e:
            log.msg("total error_info=%s, url=%s" %(e, response.url),level=log.ERROR)

    def listpare(self, response):
        if response.status == 200:
            hxs = response.selector
            datalist =  hxs.xpath("//table[@id='Resultlist']/tbody/tr[position()>1]")
            try:
                for da in datalist:
        #            name = da.select('td[2]/a/text()').extract()[0]
        #            causeserial = da.select('td[3]/text()').extract()[0]
        #            causedate = da.select('td[4]/text()').extract()[0]
                    id = da.xpath('./td[6]/a/@id').extract()[0]
                    url ="http://shixin.court.gov.cn/detail?id=%s" % id
                    yield Request(url,callback=self.detail,meta={'url':url})
            except Exception,e:
                log.msg("datalist error_info=%s, url=%s,pageNum=%s" %(e, response.url,meta['pageNum']),level=log.ERROR)
        else:
            log.msg("undowndloaded page=%s" %meta["pageNum"],level=log.ERROR) #当请求不成立的状况下记录下页数

    def detail(self,response):
        if response.status == 200:
            item =PersonMore()
            hxs = response.selector
            body = response.body
            djson = eval(body)
            print djson, "i'm djson"
            try:
                item['cid'] = djson['id']
                item['name'] = djson['iname']
                item['caseCode'] =  djson['caseCode']
                item['age'] = djson['age']
                item['sex'] = djson['sexy']
                #item['focusNumber'] = djson['focusNumber']
                item['cardNum'] = djson['cardNum']
                item['courtName'] = djson['courtName']
                item['areaName'] = djson['areaName']
                item['partyTypeName'] = djson['partyTypeName']
                item['gistId'] = djson['gistId']
                item['regDate'] = djson['regDate']
                item['gistUnit'] = djson['gistUnit']
                item['duty'] = djson['duty']
                item['performance']= djson['performance']
                item['disruptTypeName'] = djson['disruptTypeName']
                item['publishDate'] = djson['publishDate']
                #print item['cid'],item['name'],item['caseCode'],item['duty']
                #print "-------------------",item
                #yield item
            except Exception,e:
                log.msg("item error_info=%s url=%s item_key=%s" %(e, response.url,"\001".join(str(i) for i in [item.values()])), level=log.ERROR)
            yield item
        else:
            log.msg("undownloaded info url=%s"%meta["url"],level=log.ERROR)   #如果请求不成功（状态码不为200）记录下来
