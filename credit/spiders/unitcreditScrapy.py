#-*- coding:utf-8 -*-
"""
从法院官网爬失信被执行人(法人或者组织)公布的名单
"""
from scrapy.spider import Spider
from scrapy.http import Request,FormRequest
from scrapy import signals
from scrapy import log
import re
from credit.items import *
import base64

class PersonageCreditt(Spider):
    download_delay=0
    name = 'unit'
    handle_httpstatus_all = True
    writeInFile = "uniteMore"
    start_urls = ['http://shixin.court.gov.cn/unitMore.do']
    allowed_domains=['shixin.court.gov.cn']
    def __inti__(self):
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
                        callback=self.listpare,dont_filter=True,meta={'page':str(i)})
        except Exception,e:
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
                    #print name,causeserial,causedate,id
                    url ="http://shixin.court.gov.cn/detail?id=%s" % id
                    yield Request(url,callback=self.detail,meta={"url":url})
            except Exception, e:
                log.msg("datalist error_info=%s, url=%s" %(e,response.url),level=log.ERROR)
        else:
            log.msg("error page_Num=%s" %response.meta["page"],level=log.ERROR) #请求页面没有成功就记录下该页面 

    def for_ominated_data(self,in_dict, tag_str,response):
        """
        for some data are ominated
        """
        try:
            re_data = base64.b64encode(str(in_dict[tag_str]))  #base64要求转换的是字符串
        except Exception,e:
            re_data = ""    #原数据中没有该项
            log.msg("for_ominated_data error_info=%s, key=%s,url=%s" %(e,tag_str,response.url))  #记录下出现空值的项以备验查
        return re_data

    def detail(self,response):
        if response.status == 200:
            item =UnitMore()
            body = response.body
            djson = eval(body)
            #print djson
            try:
                item['cid'] = self.for_ominated_data(djson,'id',response)
                item['name'] = self.for_ominated_data(djson,'iname',response)
                item['caseCode'] = self.for_ominated_data(djson,'caseCode',response)
                item['businessEntity'] = self.for_ominated_data(djson,'businessEntity',response)
                item['cardNum'] = self.for_ominated_data(djson,'cardNum',response)
                item['courtName'] = self.for_ominated_data(djson,'courtName',response)
                item['areaName'] = self.for_ominated_data(djson,'areaName',response)
                #partytypename = djson['partyTypeName']
                item['gistId'] = self.for_ominated_data(djson,'gistId',response)
                item['regDate'] = self.for_ominated_data(djson,'regDate',response)
                item['gistUnit'] = self.for_ominated_data(djson,'gistUnit',response)
                item['duty'] = self.for_ominated_data(djson,'duty',response)
                item['performance'] = self.for_ominated_data(djson,'performance',response)
                item['disruptTypeName'] = self.for_ominated_data(djson,'disruptTypeName',response)
                item['publishDate'] = self.for_ominated_data(djson,'publishDate',response)
                #print item['cid'],item['name'],item['caseCode'],item['duty']
                #print "-------------------",item
            except Exception,e:
                log.msg("item error_info=%s, url=%s,items=%s" %(e,response.url,"\001".join([str(i) for i in item.values()])))
            yield item
        else:
            log.msg("error_detail undowload id=%s"%response.meta['url'])

