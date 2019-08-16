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
https://uland.taobao.com/sem/tbsearch?spm=a2e15.8261149.07626516003.3.290829b4n6KRSt&refpid=mm_26632258_3504122_32538762&clk1=5be22a04743bfbe9056e312b9db5d61d&keyword=%E8%A3%99%E5%AD%90&page=3&_input_charset=utf-8

"""

class TaobaoFasSpider(Spider):
    name = 'fashion_taobao_picture'
    allowed_domains = ['s.taobao.com','detail.tmall.com']

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
        super(TaobaoFasSpider, self).__init__()
        self.check_proxy_url = 'https://www.baidu.com/'
        self.merge_url = 'https://s.taobao.com'
        self.first_page_url = 'https://s.taobao.com/search?q={}&imgfile=&js=1&stats_click=search_radio_all%3A1&bcoffset=6&ntoffset=6&p4ppushleft=1%2C48&s=0'
        self.second_page_url = 'https://s.taobao.com/search?q={}&imgfile=&js=1&stats_click=search_radio_all%3A1&bcoffset=3&ntoffset=3&p4ppushleft=1%2C48&s=44'
        self.thrid_page_url = 'https://s.taobao.com/search?q={}&imgfile=&js=1&stats_click=search_radio_all%3A1&bcoffset=0&ntoffset=6&p4ppushleft=1%2C48&s=88'
        self.start_urls = 'https://s.taobao.com/search?q={0}&imgfile=&js=1&stats_click=search_radio_all%3A1&bcoffset={1}&ntoffset={2}&p4ppushleft=1%2C48&s={3}'
        self.cookies = {'miid': '471153981109237782', ' cna': '63gfFWdqoA8CAbSoONIjIbm0', ' thw': 'cn', ' UM_distinctid': '16a9a7831ca621-09143c8eb5e06c-f373567-1fa400-16a9a7831cb16d8', ' tracknick': '%5Cu6C5F%5Cu6C5F%5Cu5434%5Cu5434%5Cu7389%5Cu7389', ' tg': '0', ' hng': 'CN%7Czh-CN%7CCNY%7C156', ' t': '16f34f598154fea8f9a669b89815f170', ' _m_h5_tk': '36b253af7de76f9f3af1fe7498192623_1565870818174', ' _m_h5_tk_enc': 'fef9184ac33602085689148d3dcedb05', ' cookie2': '15a789f1925a231c3f7d331292ee20bb', ' v': '0', ' _tb_token_': 'eeed388eebb87', ' unb': '2329097405', ' uc3': 'nk2', ' csg': '8c045ad3', ' lgc': '%5Cu6C5F%5Cu6C5F%5Cu5434%5Cu5434%5Cu7389%5Cu7389', ' cookie17': 'UUtJbk9kIEI50A%3D%3D', ' dnk': '%5Cu6C5F%5Cu6C5F%5Cu5434%5Cu5434%5Cu7389%5Cu7389', ' skt': '6e6698153da4b471', ' existShop': 'MTU2NTg2MzAzMw%3D%3D', ' uc4': 'id4', ' _cc_': 'URm48syIZQ%3D%3D', ' _l_g_': 'Ug%3D%3D', ' sg': '%E7%8E%895c', ' _nk_': '%5Cu6C5F%5Cu6C5F%5Cu5434%5Cu5434%5Cu7389%5Cu7389', ' cookie1': 'BxAdKds1JL8ULOg7CMhqqntvBy0iVTtLOo4LBk3p8tk%3D', ' enc': 'x4drO4zMdDv%2Fj6%2BPp%2BoGDYjRyNnrjZFZim%2F14vnaPYdW3EJdVuADRoW9uvAJCqHAxYF1%2Fkqr85shGWynkiEnjw%3D%3D', ' mt': 'ci', ' swfstore': '101612', ' x': 'e%3D1%26p%3D*%26s%3D0%26c%3D0%26f%3D0%26g%3D0%26t%3D0%26__ll%3D-1%26_ato%3D0', ' uc1': 'cookie14', ' JSESSIONID': '6621CA4D5430DAD6DAFDE96922327237', ' whl': '-1%260%260%261565864965236', ' l': 'cBjJcJ5rv-1LkL36BOfNVZ6XDNQ9eIRb8sPPhAYpYICPObf6LH81WZe7c1LBCnGVLsteR3JM2tcgBrLEFy4Eh2nk8b8CgsDd.', ' isg': 'BD8_xgsIXiOprVvPlra89m8UzhPDIqfrC0cXUtEMaO5I4F1i2fWsF862IvC7uGs-'}

    def start_requests(self):
        # 94
        keywords = '裙子'
        bcoffset = -3
        ntoffset = -3
        s = 132
        index_ = 3
        index_s = 44
        for i in range(4,5):
            url = self.start_urls.format(keywords,bcoffset,ntoffset,s)
            bcoffset -= index_
            ntoffset -= index_
            s += index_s
            print(url)
            yield scrapy.Request(url,callback=self.parse_item,cookies=self.cookies)


    def parse_item(self,response):
        content_json = re.findall(r'g_page_config =(.*?);\n',response.body_as_unicode(),re.S)
        for item in json.loads(content_json[0])['mods']['itemlist']['data']['auctions']:
            url = 'https:'+item['detail_url']
            yield scrapy.Request(url,callback=self.parse_detail,cookies=self.cookies)


    def parse_detail(self,response):
        with open('1.html','w',encoding='utf-8') as f:
            f.write(response.body_as_unicode())
        # item = response.meta['item']
        # content = response.xpath('//div[@class="standard-body"]')
        # if content != []:
        #     img_list = response.xpath('//div[@class="standard-body"]//img/@src').extract()
        #     img_list1 = response.xpath('//div[@class="standard-body"]//img/@data-src').extract()
        #     img_list = [urljoin(self.merge_url,url) for url in img_list if not url.endswith('gif')]
        #     item['img_url_list'] = item['img_url_list'] + img_list+img_list1
        #     if 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7' in item['img_url_list']:
        #         item['img_url_list'].remove('data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7')
        #     item['img_type'] = 'dress1'
        #     yield item

            # 提取url连接
            # re.findall(r'.*g_img={url: "(http.*?jpg)"')





"""
https://s.taobao.com/search?q=%E8%A3%99%E5%AD%90&imgfile=&js=1&stats_click=search_radio_all%3A1&bcoffset=6&ntoffset=6&p4ppushleft=1%2C48&s=0
https://s.taobao.com/search?q=%E8%A3%99%E5%AD%90&imgfile=&js=1&stats_click=search_radio_all%3A1&bcoffset=3&ntoffset=3&p4ppushleft=1%2C48&s=44
https://s.taobao.com/search?q=%E8%A3%99%E5%AD%90&imgfile=&js=1&stats_click=search_radio_all%3A1&bcoffset=0&ntoffset=6&p4ppushleft=1%2C48&s=88
https://s.taobao.com/search?q=%E8%A3%99%E5%AD%90&imgfile=&js=1&stats_click=search_radio_all%3A1&bcoffset=-3&ntoffset=-3&p4ppushleft=1%2C48&s=132
https://s.taobao.com/search?q=%E8%A3%99%E5%AD%90&imgfile=&js=1&stats_click=search_radio_all%3A1&bcoffset=-6&ntoffset=-6&p4ppushleft=1%2C48&s=176
https://s.taobao.com/search?q=%E8%A3%99%E5%AD%90&imgfile=&js=1&stats_click=search_radio_all%3A1&bcoffset=-9&ntoffset=-9&p4ppushleft=1%2C48&s=220


https://item.taobao.com/item.htm?id=600063658625&ali_refid=a3_430624_1006:1214740187:N:5IQCmdrFxSHZZIIvwsEDGg%3D%3D:42f577fa92ae79788c35998355aaeacc&ali_trackid=1_42f577fa92ae79788c35998355aaeacc&spm=a21ap.7874209.10006.233

"""