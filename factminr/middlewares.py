# -*- coding: utf-8 -*-
import random
from copy import copy

from scrapy import signals
from fake_useragent import UserAgent


class FactminrSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class FactminrCrawlerMiddleware(object):
    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

    def process_start_requests(self, start_requests, spider):
        pass

    def process_request(self, request, spider):
        url = request._get_url()
        raw_url = copy(url)
        if raw_url == 'http://www.wozijideurl.com.cn':
            request._set_url('http://www.wxapp-union.com/portal.php?mod=list&catid=2&page=1')


class RandomUserAgentMiddleware(object):
    """
    利用fake_useragent生成随机请求头
    """
    def __init__(self, ua_type):
        self.ua_type = ua_type
        self.ua = UserAgent()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            ua_type=crawler.settings.get('RANDOM_UA_TYPE', 'random')
        )

    def process_request(self, request, spider):
        def get_user_agent():
            return getattr(self.ua, self.ua_type)
        request.headers.setdefault(b'User-Agent', get_user_agent())


class UserAgentMiddleware(object):
    """
    从settings配置文件读取user_agent
    """
    def __init__(self, crawler):
        super(UserAgentMiddleware, self).__init__()
        self.user_agent_list = crawler.settings.get('USER_AGENTS', [])

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_request(self, request, spider):
        user_agent = random.choice(self.user_agent_list)
        request.headers.setdefault(b'User-Agent', user_agent)
        # logger.debug("UserAgent:{}".format(user_agent))