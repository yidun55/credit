#-*- coding:utf8 -*-
#IMAGES_EXPIRES = 1000
BOT_NAME = 'credit'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['credit.spiders']
NEWSPIDER_MODULE = 'credit.spiders'
DEFAULT_ITEM_CLASS = 'credit.items.CreditItem'
ITEM_PIPELINES={'credit.pipelines.CreditPipeline':0}
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)

#LOG_FILE = '/home/dyh/data/credit/unit/log_unit_increment'

RETRY_ENABLED = False

SPIDER_MIDDLEWARES = {
    #状态码非200的响应
    'credit.middlewares.Not200Middleware': 48,
    
    #处理常见的连接超时等错误
    'credit.middlewares.RecordWrongPageMiddleware': 930
}

DOWNLOADER_MIDDLEWARES = {
    # This middleware sets the download timeout for requests specified in the DOWNLOAD_TIMEOUT setting.
    'scrapy.contrib.downloadermiddleware.downloadtimeout.DownloadTimeoutMiddleware': 350,

    # handle downloadtimeout error
    'credit.middlewares.DownloadTimeoutRetryMiddleware': 375,

    'scrapy.contrib.downloadermiddleware.redirect.RedirectMiddleware': None,
}

LOG_LEVEL = 'INFO'