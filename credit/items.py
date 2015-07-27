#coding:utf-8

from scrapy.item import Item, Field

class PersonMore(Item):
    cid = Field()
    name = Field()
    caseCode = Field()
    age = Field()
    sex = Field()
    #focusNumber = Field()
    cardNum = Field()
    courtName = Field()
    areaName = Field()
    partyTypeName = Field()
    gistId = Field()
    regDate = Field()
    gistUnit = Field()
    duty = Field()
    performance = Field()
    disruptTypeName = Field()
    publishDate = Field()
    def __init__(self, item = None):
        if item == None:
            Item.__init__(self)
            self['cid'] = 0
            self['name'] = ""
            self['caseCode'] = ""
            self['age'] = ""
            self['sex'] =  ""
            #self['focusNumber'] = ""
            self['cardNum'] = ""
            self['courtName']= ""
            self['areaName'] = ""
            self['partyTypeName'] = ""
            self['gistId'] = ""
            self['regDate'] = ""
            self['gistUnit'] = ""
            self['duty'] = ""
            self['performance'] = ""
            self['disruptTypeName'] = ""
            self['publishDate'] = ""
        else:
            Item.__init__(self,item)
class UnitMore(Item):
    cid = Field()
    name = Field()
    caseCode = Field()
    cardNum = Field()
    businessEntity = Field()
    courtName = Field()
    areaName = Field()
    gistId = Field()
    regDate = Field()
    gistUnit = Field()
    duty = Field()
    performance = Field()
    disruptTypeName = Field()
    publishDate = Field()
    def __init__(self, item = None):
        if item == None:
            Item.__init__(self)
            self['cid'] = 0
            self['name'] = ""
            self['caseCode'] = ""
            self['cardNum'] = ""
            self['businessEntity'] = ""
            self['courtName']= ""
            self['areaName'] = ""
            self['gistId'] = ""
            self['regDate'] = ""
            self['gistUnit'] = ""
            self['duty'] = ""
            self['performance'] = ""
            self['disruptTypeName'] = ""
            self['publishDate'] = ""
        else:
            Item.__init__(self,item)

class IdItem(Item):
    """
    用于存贮id
    """
    content = Field()
