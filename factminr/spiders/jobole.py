# -*- coding: utf-8 -*-
import scrapy
import logging
from selenium import webdriver
from scrapy import signals
from pydispatch import dispatcher

logger = logging.getLogger(__name__)


class JoboleSpider(scrapy.Spider):
    name = 'jobole'
    allowed_domains = ['sse.com.cn']
    start_urls = ['http://www.sse.com.cn/disclosure/listedinfo/announcement/']
    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "DNT": "1",
            "Host": "www.sse.com.cn",
            "Pragma": "no-cache",
            # "Referer": "http://www.sse.com.cn/disclosure/listedinfo/regular/",
            "Upgrade-Insecure-Requests": "1",
        },
        'DOWNLOADER_MIDDLEWARES': {
            'factminr.middlewares.UserAgentMiddleware': 200,
            'factminr.middlewares.JspageMiddleware': 20,
        },
    }

    def __init__(self):
        self.browser = webdriver.Chrome()
        super(JoboleSpider, self).__init__()
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    # 当爬虫关闭的时候关闭chrome
    def spider_closed(self, spider):
        logger.info("spider closed")
        self.browser.close()

    def parse(self, response):
        urls = response.css('dl[class=modal_pdf_list] dd a::attr(href)').getall()
        print(urls)