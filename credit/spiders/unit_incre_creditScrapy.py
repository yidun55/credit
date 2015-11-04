#-*- coding:utf-8 -*-
"""
从法院官网爬失信被执行人(法人或者组织)公布的名单
"""
from scrapy.spider import Spider
from scrapy.http import Request,FormRequest
from scrapy.utils.request import request_fingerprint
from scrapy import signals
import logging
import re
from credit.items import *
import base64
import time

class PersonageCreditt(Spider):
    download_delay=1
    name = 'unit_incre'
    handle_httpstatus_all = True
    writeInFile = "/home/dyh/data/credit/unit/unit_%s.txt"
    # writeInFile = "E:/DLdata/unit_2015_10_27.txt"
    controlFile = "/home/dyh/data/credit/unit/unit_control.txt"
    # controlFile = "E:/DLdata/unit_control.txt"
    start_urls = ['http://shixin.court.gov.cn/unitMore.do']
    allowed_domains=['shixin.court.gov.cn']
    order = ["cid","name","caseCode","businessEntity",\
       "cardNum","courtName","areaName","gistId","regDate",\
       "gistUnit","duty","performance","disruptTypeName",\
       "publishDate"] 

    def __init__(self):
        self.file_handler = open(self.writeInFile%time.strftime("%Y_%m_%d"), "a")
        self.file_control = open(self.controlFile, "a+")
        self.url_have_seen = "dup_unit"
        for line in self.file_control:
            try:
                fp = self.url_fingerprint(line)
                self.myRedis.sadd(self.url_have_seen,fp)
            except Exception, e:
                logging.ERROR("__init__ url=%s, e=%s"%(line.strip(),e))         

    def url_fingerprint(self, url):
        req = Request(url.strip())
        fp = request_fingerprint(req)
        return fp 

    def make_requests_from_url(self,url):
        return Request( url, callback=self.gettotal,dont_filter=True )

    def gettotal(self,response):
        hxs = response.selector
        try:
            total = 7107
            url = "http://shixin.court.gov.cn/unitMore.do"
            for i in range(1,total+1)[0:2]:
                yield FormRequest(url,
                        formdata={'currentPage': str(i)},
                        headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'},
                        callback=self.listpare,dont_filter=False,meta={'page':str(i)})
        except Exception,e:
            logging.ERROR("total error_info=%s, url=%s" %(e, response.url))

    def listpare(self, response):
        if response.status == 200:
            hxs = response.selector
            datalist =  hxs.xpath("//table[@id='Resultlist']/tbody/tr[position()>1]")
            try:
                for da in datalist:
                    id = da.xpath('./td[6]/a/@id').extract()[0]
                    url ="http://shixin.court.gov.cn/detail?id=%s" % id
                    fp = self.url_fingerprint(url)
                    isexist = self.myRedis.sadd(self.url_have_seen,fp)
                    if isexist:
                        #如果redis set ppai_dup_redis没有则插入并返回1，否则
                        #返回0
                        yield Request(url,callback=self.detail,meta={'url':url})
                    else:
                        pass
                    
            except Exception, e:
                logging.ERROR("datalist error_info=%s, url=%s" %(e,response.url))
        else:
            logging.ERROR("error page_Num=%s" %response.meta["page"]) #请求页面没有成功就记录下该页面 

    def for_ominated_data(self,in_dict, tag_str,response):
        """
        for some data are ominated
        """
        try:
            re_data = base64.b64encode(str(in_dict[tag_str]))  #base64要求转换的是字符串
        except Exception,e:
            re_data = ""    #原数据中没有该项
            logging.ERROR("for_ominated_data error_info=%s, key=%s,url=%s" %(e,tag_str,response.url))  #记录下出现空值的项以备验查
        return re_data

    def detail(self,response):
        if response.status == 200:
            # item =UnitMore()
            item = simpleItem()
            con_dict = {}
            body = response.body
            self.file_control.write(response.url+"\n") #请求成功的url记录起来
            djson = eval(body)
            try:
                con_dict['cid'] = self.for_ominated_data(djson,'id',response)
                con_dict['name'] = self.for_ominated_data(djson,'iname',response)
                con_dict['caseCode'] = self.for_ominated_data(djson,'caseCode',response)
                con_dict['businessEntity'] = self.for_ominated_data(djson,'businessEntity',response)
                con_dict['cardNum'] = self.for_ominated_data(djson,'cardNum',response)
                con_dict['courtName'] = self.for_ominated_data(djson,'courtName',response)
                con_dict['areaName'] = self.for_ominated_data(djson,'areaName',response)
                #partytypename = djson['partyTypeName']
                con_dict['gistId'] = self.for_ominated_data(djson,'gistId',response)
                con_dict['regDate'] = self.for_ominated_data(djson,'regDate',response)
                con_dict['gistUnit'] = self.for_ominated_data(djson,'gistUnit',response)
                con_dict['duty'] = self.for_ominated_data(djson,'duty',response)
                con_dict['performance'] = self.for_ominated_data(djson,'performance',response)
                con_dict['disruptTypeName'] = self.for_ominated_data(djson,'disruptTypeName',response)
                con_dict['publishDate'] = self.for_ominated_data(djson,'publishDate',response)
                con = []
                for i in self.order:
                    con.append(con_dict[i])
                item["con"] = "\001".join(con) + "\n"
            except Exception,e:
                logging.ERROR("item error_info=%s, url=%s,items=%s" %(e,response.url,"\001".join([str(i) for i in item.values()])))
            yield item
        else:
            logging.ERROR("error_detail undowload id=%s"%response.meta['url'])



# ["cid","name","caseCode","businessEntity","cardNum","courtName","areaName","gistId","regDate","gistUnit","duty","performance","disruptTypeName","publishDate"]   #writeIn for unitMore
