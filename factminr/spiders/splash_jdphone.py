# -*- coding: utf-8 -*-
"""
利用splash，爬取京东手机信息
"""
import scrapy
from scrapy_splash.request import SplashRequest


class SplashJdspider(scrapy.Spider):
    name = 'splash_jdphone'
    start_urls = ['https://item.jd.com/100000177760.html']

    custom_settings = {
        'DEFAULT_REQUEST_HEADERS ': {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "cache-control": "no-cache",
            "dnt": "1",
            "pragma": "no-cache",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
        },
        'SPIDER_MIDDLEWARES': {
            'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
        },
        'DOWNLOADER_MIDDLEWARES': {
            'factminr.middlewares.UserAgentMiddleware': 200,
            'scrapy_splash.SplashCookiesMiddleware': 723,
            'scrapy_splash.SplashMiddleware': 725,
            'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
        },
        'SPLASH_URL': 'http://192.168.99.100:8050/',
        'DUPEFILTER_CLASS': 'scrapy_splash.SplashAwareDupeFilter',  # 设置Splash自己的去重过滤器
        'HTTPCACHE_STORAGE': 'scrapy_splash.SplashAwareFSCacheStorage',  # 使用Splash的Http缓存
        'DOWNLOAD_TIMEOUT': '20',  # 下载超时时间默认180
        'RETRY_ENABLED': 'True',
        'RETRY_TIMES': '9',  # 重试次数，默认在此基础加1
    }

    def start_requests(self):
        """
        搜索京东手机入口
        :return:
        """
        for url in self.start_urls:
            yield SplashRequest(
                url=url,
                callback=self.parse,
                args={'wait': 0.5},
            )

    def parse(self, response):
        """
        解析搜索结果
        :param response:
        :return:
        """
        select = scrapy.Selector(text=response.text)
        price = select.css('span[class=p-price] span:nth-child(2)::text').get()
        # price = select.xpath('//span[@class="p-price"]/span[2]/text()').get()
        print(price)