# -*- coding: utf-8 -*-
import scrapy
import pymongo
from scrapy.pipelines.images import ImagesPipeline, FilesPipeline
import logging
from scrapy.exceptions import DropItem

logger = logging.getLogger(__name__)


class FactminrPipeline(object):
    """
    数据清洗
    """
    def process_item(self, item, spider):
        front_image = item.get('front_image')
        item['front_image'] = "".join(front_image)
        return item


class WxappImagePipeline(ImagesPipeline):
    """
    wxapp下载图片的管道文件
    """
    def item_completed(self, results, item, info):
        for ok, value in results:
            # print(ok)  # 返回布尔
            # print(value)  # 字典
            if ok:
                front_img_url = value.get('url')  # 图片下载链接
                front_img_file_path = value.get('path')  # 图片保存路径
                front_img_uuid = value.get('checksum')  # 图片去重标识
                item['img_file_path'] = front_img_file_path
                item['img_uuid'] = front_img_uuid
                item['img_url'] = front_img_url
                return item
            else:
                logger.debug('获取不到列表页图片')
                return item


class MyFilesPipeline(FilesPipeline):
    """
    文件下载，管道文件
    """

    def get_media_requests(self, item, info):
        file_url = item.get('file_url', '')
        if file_url.endswith('pdf'):
            yield scrapy.Request(file_url)

        elif file_url.endswith('doc'):
            yield scrapy.Request(file_url)

        else:
            logger.info('既不是PDF也不是word纯文本')

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            logger.debug('不是PDF文件格式，是纯文本格式')
            item['cf_file_name'] = ''
            # raise DropItem("Item contains no files")
        else:
            item['cf_file_name'] = image_paths[0]
        return item


class MongodbPipeline(object):
    """
   存储到mongodb
   """

    def __init__(self, mongo_uri, mongo_db):
        self.client = pymongo.MongoClient(mongo_uri)
        self.db = self.client[mongo_db]

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATA_BASE')
        )

    def process_item(self, item, spider):
        collection = self.db[spider.name]
        collection.insert(dict(item))
        # collection.update({'uuid': item['uuid']}, dict(item), True)
        # logger.info("数据插入成功:%s"%item)
        return item

    def close_spider(self, spider):
        self.client.close()