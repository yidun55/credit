#-*- coding:utf-8 -*-
"""
从法院官网爬失信被执行人(法人或者组织)公布的名单
"""
from scrapy.spider import Spider
from scrapy.http import Request,FormRequest
from scrapy import signals
from scrapy import log
from scrapy import Selector
import re
from credit.items import *
import base64
import time

class PersonageCreditt(Spider):
    download_delay=0
    name = 'unit_increment'
    last_update_date = '2015年07月22日'  #已有数据的最新更新日期
    page = 1    #记录已经请求的页面数
    handle_httpstatus_all = True
    writeInFile = "uniteMore"
    start_urls = ['http://shixin.court.gov.cn/unitMore.do']
    allowed_domains=['shixin.court.gov.cn']
    def __init__(self):
        pass

    def make_requests_from_url(self,url):
        return Request(url, callback=self.gettotal,dont_filter=True )

    def gettotal(self,response):
        if response.status == 200:
            tm_struct = time.strptime(self.last_update_date,'%Y年%m月%d日')
            last_update_stamp = time.mktime(tm_struct) #将已有数据更新时间换成时间截
            sel = Selector(text=response.body)
            datalist =  sel.xpath("//table[@id='Resultlist']/tbody/tr[position()>1]")
            try:
                a = last_update_stamp #记录本次页面的最早的更新时间
                reqs = []  #贮存请求
                for da in datalist:
                    causedate = da.select('td[4]/text()').extract()[0]
                    tm_struct = time.strptime(causedate,'%Y年%m月%d日')
                    update_stamp = time.mktime(tm_struct)
                    if update_stamp > last_update_stamp:   #如果da中的更新时间晚于已有数据的更新时间则提取id并发出请求
                        id = da.xpath('./td[6]/a/@id').extract()[0]
                        url ="http://shixin.court.gov.cn/detail?id=%s" % id
                        req = Request(url,callback=self.detail,meta={"url":url})
                        reqs.append(req)
                    else:
                        break
                    self.page += 1
                    req = FormRequest(response.url,
                            formdata={'currentPage': str(self.page)},
                            headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'},
                            callback=self.gettotal,dont_filter=True,meta={'page':str(i)})
                    reqs.insert(0, req)
                    for req in reqs:
                        yield req

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

