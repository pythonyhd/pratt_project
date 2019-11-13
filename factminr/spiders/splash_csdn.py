# -*- coding: utf-8 -*-
import scrapy
from scrapy_splash.request import SplashRequest


# splash lua script
script ="""
        function main(splash, args)
            splash:go(args.url)
            local scroll_to = splash:jsfunc("window.scrollTo")
            scroll_to(0, 2800)
            splash:set_viewport_full()
            splash:wait(5)
            return {html=splash:html()}
        end
"""


class SplashWithlua(scrapy.Spider):
    name = 'splash_csdn'
    start_urls = ['www.baidu.com']
    url = 'https://blog.csdn.net/'

    custom_settings = {
        # 'DEFAULT_REQUEST_HEADERS': {},
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
        yield SplashRequest(
            endpoint='execute',
            args={'lua_source': script, 'url': self.url},
        )

    def parse(self, response):
        title = response.xpath('//div[@class="title"]/h2/a[1]/text()').getall()
        print(title)