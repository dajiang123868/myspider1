import os
from pprint import pprint
from urllib.parse import urljoin, urlencode

import scrapy
import time
from scrapy.spiders import CrawlSpider, Rule, Spider
from scrapy.linkextractors import LinkExtractor
import logging
import requests
import json
from lxml import etree
import re
from main_spider.settings import IMAGES_STORE
from main_spider.items import DownloadpictureItem
"""
https://www.elle.com/fashion/
"""

class EleeFasSpider(Spider):
    name = 'fashion_elle_picture'
    allowed_domains = ['elle.com']

    custom_settings = dict(
        # JOBDIR =  'job_info/001',
        # CONCURRENT_REQUESTS=100,
        DEFAULT_REQUEST_HEADERS={
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            # 'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'
        },
        DOWNLOADER_MIDDLEWARES={
            'main_spider.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'main_spider.middlewares.RandomUserAgentMiddleware': 100,
            # 'main_spider.middlewares.ProxyMiddleware': 200,

        },
        ITEM_PIPELINES={
            'main_spider.pipelines.DownImgloadPipeline': 100,
            # 'main_spider.pipelines.MongoPipeline': 200,

        },
        DOWNLOAD_DELAY=0,
        ROBOTSTXT_OBEY=False,
        IMAGES_STORE = IMAGES_STORE,
        IMAGES_EXPIRES = 365,
        IMAGES_MIN_HEIGHT = 110,
        IMAGES_MIN_WIDTH = 110
        # ip并发量
        # CONCURRENT_REQUESTS_PER_IP = 1,
        # 每次请求数量
        # CONCURRENT_REQUESTS_PER_DOMAIN = 1
        # 除非真的需要否则就禁止cookies
        # COOKIES_ENABLED=False
        # LOG_FILE="LOG_INFO/cena.log",
        # 禁止重试遇到错误不在retry
        # RETRY_ENABLED=False
        # LOG_LEVEL="INFO",
        # AJAXCRAWL_ENABLED=True
        # DEPTH_LIMIT=0
        # allow_redirects=False
    )

    def __init__(self):
        super(EleeFasSpider, self).__init__()
        self.check_proxy_url = 'https://www.baidu.com/'
        self.merge_url = 'https://www.elle.com'

    def start_requests(self):
        # 94
        for i in range(1,94):
            url = 'https://www.elle.com/ajax/infiniteload/?id=search&class=CoreModels\search\TagQueryModel&viewset=search&trackingId=search-results&trackingLabel=dress&params={%22input%22:%22dress%22,%22page_size%22:42}&page='+str(i)+'&cachebuster='
            yield scrapy.Request(url,callback=self.parse_item)


    def parse_item(self,response):
        nodes_list = response.xpath('//div[@class="feed feed-grid"]/div')
        if nodes_list != []:
            for node in nodes_list:
                item = DownloadpictureItem()
                part_url = node.xpath('.//a[@class="simple-item-title item-title"]/@href').extract_first()
                if part_url:
                    img_url_list = []
                    url = urljoin(self.merge_url,part_url)
                    img_url = urljoin(self.merge_url,node.xpath('.//img[@class="lazyimage lazyload"]/@data-src').extract_first())
                    title = node.xpath('.//a[@class="simple-item-title item-title"]').xpath('string(.)').extract_first().replace('\n','')
                    if img_url:
                        img_url_list.append(img_url)
                    item['url'] = url
                    item['img_url_list'] = img_url_list
                    item['title'] = title
                    yield scrapy.Request(item['url'],callback=self.parse_detail,meta={'item':item})


    def parse_detail(self,response):
        item = response.meta['item']
        content = response.xpath('//div[@class="standard-body"]')
        if content != []:
            img_list = response.xpath('//div[@class="standard-body"]//img/@src').extract()
            img_list1 = response.xpath('//div[@class="standard-body"]//img/@data-src').extract()
            img_list = [urljoin(self.merge_url,url) for url in img_list if not url.endswith('gif')]
            item['img_url_list'] = item['img_url_list'] + img_list+img_list1
            if 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7' in item['img_url_list']:
                item['img_url_list'].remove('data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7')
            item['img_type'] = 'dress1'
            yield item

            # 提取url连接
            # re.findall(r'.*g_img={url: "(http.*?jpg)"')





