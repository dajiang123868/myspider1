# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import hashlib
import json

from scrapy.utils.python import to_bytes

import pymongo
import scrapy
from scrapy.pipelines.images import ImagesPipeline

from main_spider.items import DownloadpictureItem

from main_spider.settings import IMAGES_STORE
import os


class MongoPipeline(object):
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DB')
        )

    def open_spider(self, spider):

        pass
        # self.client = pymongo.MongoClient(self.mongo_uri)
        # self.db = self.client[self.mongo_db]

    def process_item(self, item, spider):
        # self.db[item.collection].insert(dict(item))
        return item

    def close_spider(self, spider):
        pass
        # self.client.close()



class DownImgloadPipeline(ImagesPipeline):
    """docstring for DoubanDownloadPipeline"""

    def get_media_requests(self, item, info):
        default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36'
        }

        item['img_path'] = []
        if isinstance(item, DownloadpictureItem) and item.get('img_url_list') != []:
            for img_url in item['img_url_list']:
                yield scrapy.Request(img_url,headers=default_headers,meta={"item":item})


    def file_path(self, request, response=None, info=None):
        item = request.meta["item"]
        # 再从item中取出分类名称,这个name就是我们想自定义图片路径的文件名称,(如果不自定义file_path函数的话,默认会将图片下载到full文件里)
        name = item['img_type']
        image_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        # 再从item中取出img_url,分隔出来图片的名称.图片的网址一般最后一个'/'后都是数字,此处用它作图片的名字
        img_url_name = image_guid +'.jpg'
        return "%s/%s" % (name, img_url_name)
        # print(request)

    def item_completed(self, results, item, info):
        index = [index for index in range(len(results)) if not results[index][0]]
        image_paths = [os.path.join(IMAGES_STORE,info.get('path', None)) for success, info in results if success and info]
        if index != []:
            x = 0
            for i in index:

                item['img_url_list'].pop(i-x)
                x += 1
            return item
        if isinstance(item, DownloadpictureItem):
            item['img_path'] = image_paths
            with open('D:\\test_code\myspider1\main_spider\main_spider\\util\data.txt','a+',encoding='utf-8') as f:
                f.write(json.dumps(dict(item),ensure_ascii=False)+'\n')
            print('保存了')

        return item


