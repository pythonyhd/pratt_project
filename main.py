# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 11:47
# @Author  : Yasaka.Yu
# @File    : main.py
from scrapy import cmdline


# cmdline.execute('scrapy crawl wxapp'.split())  # 不下载列表页图片
# cmdline.execute('scrapy crawl wxapp_with_img'.split())  # 下载列表页图片
# cmdline.execute('scrapy crawl wxapp_signal'.split())  # 测试偏移量
# cmdline.execute('scrapy crawl szse_spider'.split())  # 深圳证券交易所-监管信息公开-监管措施与纪律处分
# cmdline.execute('scrapy crawl splash_jdphone'.split())  # spalsh抓取京东手机信息
# cmdline.execute('scrapy crawl splash_lua'.split())  # spalsh结合lua脚本使用
# cmdline.execute('scrapy crawl splash_csdn'.split())  # spalsh结合lua脚本滑动csdn
cmdline.execute('scrapy crawl jobole'.split())  # selenium集成