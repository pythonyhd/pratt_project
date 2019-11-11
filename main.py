# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 11:47
# @Author  : Yasaka.Yu
# @File    : main.py
from scrapy import cmdline


# cmdline.execute('scrapy crawl wxapp'.split())  # 不下载列表页图片
# cmdline.execute('scrapy crawl wxapp_with_img'.split())  # 下载列表页图片
cmdline.execute('scrapy crawl wxapp_signal'.split())