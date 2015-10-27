#-*- coding:utf-8 -*-
"""
从法院官网爬被执行人公布的名单
"""
from scrapy.spider import Spider
from scrapy.http import Request,FormRequest
from scrapy.utils.request import request_fingerprint
from scrapy import signals
from scrapy import log
import re
from credit.items import *
import base64

class PersonageCreditt(Spider):
    download_delay=1
    name = 'person_incre'
    handle_httpstatus_all = True
    writeInFile = "/home/dyh/data/credit/person/person_2015_10_27.txt"
    # writeInFile = "E:/DLdata/person_2015_10_27.txt"
    controlFile = "/home/dyh/data/credit/person/person_control.txt"
    # controlFile = "E:/DLdata/person_control.txt"
    start_urls = ['http://shixin.court.gov.cn/personMore.do']
    allowed_domains=['shixin.court.gov.cn']
    order = ["cid","name","caseCode","age","sex",\
        "cardNum","courtName","areaName","partyTypeName",\
        "gistId","regDate","gistUnit","duty","performance",\
        "disruptTypeName","publishDate"] #writeIn for personMore
    def __init__(self):
        pass

    def set_crawler(self,crawler):
        super(PersonageCreditt, self).set_crawler(crawler)
        self.bind_signal()


    def bind_signal(self):
        self.crawler.signals.connect(self.open_file, \
            signal=signals.spider_opened)  #爬虫开启时，打开文件
        self.crawler.signals.connect(self.close_file, \
            signal=signals.spider_closed)  #爬虫关闭时，关闭文件

    def open_file(self):
        self.file_handler = open(self.writeInFile, "a")
        self.file_control = open(self.controlFile, "a+")
        self.url_have_seen = set()
        for line in self.file_control:
            fp = self.url_fingerprint(line)
            self.url_have_seen.add(fp)        

    def url_fingerprint(self, url):
        req = Request(url.strip())
        fp = request_fingerprint(req)
        return fp 

    def close_file(self):
        self.file_handler.close()

    def make_requests_from_url(self,url):
        return Request( url, callback=self.gettotal,dont_filter=True )

    def gettotal(self,response):
        hxs = response.selector
        try:
            # total = hxs.xpath(u"//a[contains(text(),'尾页')]/@onclick").extract()[0]
            # total = int(re.findall("\d+",total)[0])
            total = 40000   #页数
            url = "http://shixin.court.gov.cn/personMore.do"
            for i in range(1,total+1)[0:2]:
                yield FormRequest(url,
                        formdata={'currentPage': str(i)},
                        headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'},
                        callback=self.listpare,dont_filter=True, meta={'pageNum':str(i)})
        except Exception, e:
            log.msg("total error_info=%s, url=%s" %(e, response.url),level=log.ERROR)

    def listpare(self, response):
        if response.status == 200:
            hxs = response.selector
            datalist =  hxs.xpath("//table[@id='Resultlist']/tbody/tr[position()>1]")
            if len(datalist) == 0:
                log.msg("datalist_empty error_info, url=%s,pageNum=%s" %(response.url,response.meta['pageNum']),level=log.ERROR)
            try:
                for da in datalist:
                    id = da.xpath('./td[6]/a/@id').extract()[0]
                    url ="http://shixin.court.gov.cn/detail?id=%s" % id
                    fp = self.url_fingerprint(url)
                    if fp not in self.url_have_seen:
                        self.url_have_seen.add(fp)
                        yield Request(url,callback=self.detail,meta={'url':url})
                    else:
                        pass


            except Exception,e:
                log.msg("datalist error_info=%s, url=%s,pageNum=%s" %(e, response.url,meta['pageNum']),level=log.ERROR)
        else:
            log.msg("undowndloaded page=%s" %meta["pageNum"],level=log.ERROR) #当请求不成立的状况下记录下页数
    
    def for_ominated_data(self,in_dict, tag_str,response):
        """
        for some data are ominated
        """
        try:
            re_data = base64.b64encode(str(in_dict[tag_str]))  #base64要求转换的是字符串 for test
            # re_data = str(in_dict[tag_str])
        except Exception,e:
            re_data = ""    #原数据中没有该项
            log.msg("for_ominated_data error_info=%s, key=%s,url=%s" %(e,tag_str,response.url))  #记录下出现空值的项以备验查
        return re_data

    def detail(self,response):
        if response.status == 200:
            # item =PersonMore()
            con_dict = {}
            item = simpleItem()
            self.file_control.write(response.url+"\n")
            body = response.body
            djson = eval(body)
            try:
                con_dict['cid'] = self.for_ominated_data(djson, 'id', response)
                con_dict['name'] = self.for_ominated_data(djson, 'iname', response)
                con_dict['caseCode'] =  self.for_ominated_data(djson, 'caseCode', response)
                con_dict['age'] = self.for_ominated_data(djson, 'age',response)
                con_dict['sex'] = self.for_ominated_data(djson, 'sexy', response)
                #con_dict['focusNumber'] = djson['focusNumber']
                con_dict['cardNum'] = self.for_ominated_data(djson, 'cardNum',response)
                con_dict['courtName'] = self.for_ominated_data(djson, 'courtName', response)
                con_dict['areaName'] = self.for_ominated_data(djson, 'areaName', response)
                con_dict['partyTypeName'] = self.for_ominated_data(djson, 'partyTypeName', response)
                con_dict['gistId'] = self.for_ominated_data(djson, 'gistId', response)
                con_dict['regDate'] = self.for_ominated_data(djson, 'regDate', response)
                con_dict['gistUnit'] = self.for_ominated_data(djson, 'gistUnit', response)
                con_dict['duty'] = self.for_ominated_data(djson, 'duty', response)
                con_dict['performance']= self.for_ominated_data(djson, 'performance', response)
                con_dict['disruptTypeName'] = self.for_ominated_data(djson, 'disruptTypeName', response)
                con_dict['publishDate'] = self.for_ominated_data(djson,'publishDate',response)
                con = []
                for i in self.order:
                    con.append(con_dict[i])
                item["con"] = "\001".join(con) + "\n"
            except Exception,e:
                log.msg("item error_info=%s url=%s item_key=%s" %(e, response.url,"\001".join(str(i) for i in [item.values()])), level=log.ERROR)
            yield item
        else:
            log.msg("undownloaded info url=%s"%meta["url"],level=log.ERROR)   #如果请求不成功（状态码不为200）记录下来


