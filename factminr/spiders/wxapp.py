# -*- coding: utf-8 -*-
import re
from functools import reduce

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from urllib.parse import urljoin


class WxappSpider(CrawlSpider):
    name = 'wxapp'
    allowed_domains = ['wxapp-union.com']
    start_urls = ['http://www.wxapp-union.com/portal.php?mod=list&catid=2&page=1']

    rules = (
        # Rule(LinkExtractor(allow=r'.+mod=list&catid=2&page=\d+', unique=False), follow=True),
        Rule(LinkExtractor(allow=r'.+mod=list&catid=2&page=\d+'), callback='parse_index', follow=True),
        Rule(LinkExtractor(allow=r'.+article.+\.html'), callback='parse_details', follow=False),
    )

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'factminr.middlewares.RandomUserAgentMiddleware': 120,
            # 'factminr.middlewares.UserAgentMiddleware': 130,
        },
        'ITEM_PIPELINES': {
            'factminr.pipelines.MongodbPipeline': 320,  # 保存到mongodb
        },
    }

    # 动态域设置
    # def __init__(self, *args, **kwargs):
    #     """设置动态域只能抓取网站允许抓取得内容"""
    #     domain = kwargs.pop('domain', '')
    #     self.allowed_domains = filter(None, domain.split(','))
    #     super(WxappSpider, self).__init__(*args, **kwargs)

    def parse_details(self, response):
        """
        详情页解析
        :param response:
        :return:
        """
        re_com = re.compile(r'\r|\n|\t|\s')
        selector = scrapy.Selector(text=response.text)
        title = selector.css('.ph::text').get(default='').strip()
        publish_time = selector.css('.time::text').get(default='').strip()
        view_count = selector.css('div[class*=focus_num] a::text').get('').strip()
        content_list = selector.xpath('//td[@id="article_content"]//text()').getall()
        content = reduce(lambda x, y: x+y, [re_com.sub('', i) for i in content_list])
        img_url_list = selector.xpath('//td[@id="article_content"]//a/img/@src').getall()
        if img_url_list:
            img_url = [urljoin('http://www.wxapp-union.com/', img_url) for img_url in list(set(img_url_list))]
        else:
            img_url = []
        wechat_item = dict(
            title=title,
            publish_time=publish_time,
            view_count=view_count,
            content=content,
            img_urls=img_url,  # 详情页的url
            url=response.url,
        )
        # print(wechat_item)
        yield wechat_item