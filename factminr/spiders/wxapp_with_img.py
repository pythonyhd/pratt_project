# -*- coding: utf-8 -*-
import re
from functools import reduce
from urllib.parse import urljoin

import scrapy


class WxappWithImage(scrapy.Spider):
    name = 'wxapp_with_img'
    start_urls = ['http://www.wxapp-union.com/portal.php?mod=list&catid=2&page=1']
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'factminr.middlewares.RandomUserAgentMiddleware': 120,
            # 'factminr.middlewares.UserAgentMiddleware': 130,
        },
        'ITEM_PIPELINES': {
            'factminr.pipelines.WxappImagePipeline': 300,  # 下载列表页图片
            # 'factminr.pipelines.FactminrPipeline': 320,  # 数据清洗
            'factminr.pipelines.MongodbPipeline': 340,  # 保存到mongodb
        },
        'IMAGES_URLS_FIELD': 'front_image',
    }

    def parse(self, response):
        """
        解析列表，翻页
        :param response:
        :return:
        """
        # 解析
        selector = scrapy.Selector(text=response.text)
        # selector.css('.shout').xpath('./time/@datetime').extract()  # 可以嵌套xpath跟css一起使用
        base_nodes = selector.css('div[class*=mbox_list]')
        for node in base_nodes:
            link = node.css('a::attr(href)').get()  # 详情
            img_url = node.css('a img::attr(src)').get()  # 列表文章图片
            url = urljoin(response.url, link)
            front_image = urljoin(response.url, img_url)
            # print(f'详情页url={url}')
            # print(f'列表图片url={front_image}')
            yield scrapy.Request(
                url=url,
                callback=self.parse_details,
                priority=5,
                meta={'front_image': front_image},
            )
        # 翻页
        next_url = response.css('.nxt::attr(href)').get()
        if next_url:
            yield scrapy.Request(
                url=next_url,
                priority=3,
            )

    def parse_details(self, response):
        """
        详情页解析
        :param response:
        :return:
        """
        front_image = response.meta.get('front_image', '')
        selector = scrapy.Selector(text=response.text)
        title = selector.css('.ph::text').get(default='').strip()
        publish_time = selector.css('.time::text').get(default='').strip()
        view_count = selector.css('div[class*=focus_num] a::text').get('').strip()
        content_list = selector.xpath('//td[@id="article_content"]//text()').getall()
        re_com = re.compile(r'\r|\n|\t|\s')
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
            detail_img_urls=img_url,  # 详情页的url
            url=response.url,
            front_image=[front_image],
        )
        # print(wechat_item)
        yield wechat_item