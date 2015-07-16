#-*- coding:utf8 -*-
#IMAGES_EXPIRES = 1000
BOT_NAME = 'credit'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['credit.spiders']
NEWSPIDER_MODULE = 'credit.spiders'
DEFAULT_ITEM_CLASS = 'credit.items.CreditItem'
ITEM_PIPELINES=['credit.pipelines.CreditPipeline']
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)

LOG_FILE = '/home/dyh/data/credit/person/log_personMore'
