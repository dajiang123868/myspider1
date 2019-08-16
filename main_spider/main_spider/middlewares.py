# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import random
import logging
import re

import scrapy
from scrapy import signals
from scrapy.pipelines.images import ImagesPipeline
from twisted.internet import defer
from twisted.internet.error import TimeoutError, DNSLookupError, \
    ConnectionRefusedError, ConnectionDone, ConnectError, \
    ConnectionLost, TCPTimedOutError
from twisted.web.client import ResponseFailed

from scrapy.core.downloader.handlers.http11 import TunnelError

from main_spider.util.proxy import get_one_proxy

from main_spider.util.proxy import get_valid_proxy_pool


class MainSpiderSpiderMiddleware(object):
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

        # Should return either None or an iterable of Response, dict
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


class MainSpiderDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)



class RandomUserAgentMiddleware():
    '''
    代理UA中间件:电脑端
    '''

    def __init__(self):
        self.user_agents = [
            "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/532.5 (KHTML, like Gecko) Chrome/4.0.249.0 Safari/532.5",
            "Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US) AppleWebKit/532.9 (KHTML, like Gecko) Chrome/5.0.310.0 Safari/532.9",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.7 (KHTML, like Gecko) Chrome/7.0.514.0 Safari/534.7",
            "Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/534.14 (KHTML, like Gecko) Chrome/9.0.601.0 Safari/534.14",
            "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.14 (KHTML, like Gecko) Chrome/10.0.601.0 Safari/534.14",
            "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.20 (KHTML, like Gecko) Chrome/11.0.672.2 Safari/534.20",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.27 (KHTML, like Gecko) Chrome/12.0.712.0 Safari/534.27",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.24 Safari/535.1",
            "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.874.120 Safari/535.2",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.36 Safari/535.7",
            "Mozilla/5.0 (Windows; U; Windows NT 6.0 x64; en-US; rv:1.9pre) Gecko/2008072421 Minefield/3.0.2pre",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.10) Gecko/2009042316 Firefox/3.0.10",
            "Mozilla/5.0 (Windows; U; Windows NT 6.0; en-GB; rv:1.9.0.11) Gecko/2009060215 Firefox/3.0.11 (.NET CLR 3.5.30729)",
            "Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6 GTB5",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; tr; rv:1.9.2.8) Gecko/20100722 Firefox/3.6.8 ( .NET CLR 3.5.30729; .NET4.0E)",
            "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
            "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
            "Mozilla/5.0 (Windows NT 5.1; rv:5.0) Gecko/20100101 Firefox/5.0",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0a2) Gecko/20110622 Firefox/6.0a2",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:7.0.1) Gecko/20100101 Firefox/7.0.1",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:2.0b4pre) Gecko/20100815 Minefield/4.0b4pre",
        ]

    def process_request(self, request, spider):
        if not request.headers.get('User-Agent'):
            request.headers['User-Agent'] = random.choice(self.user_agents)


class MobileRandomUserAgentMiddleware():
    '''
    代理UA中间件:手机H5端
    '''

    def __init__(self):
        self.user_agents = [
            "Mozilla/5.0 (Linux; Android 4.4.4; HTC D820u Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.89 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; U; Android 4.4.4; zh-cn; HTC_D820u Build/KTU84P) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12A365 Safari/600.1.4",
            "UC:Mozilla/5.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X; zh-CN) AppleWebKit/537.51.1 (KHTML, like Gecko)",
            "Mozilla/5.0 (Linux; U; Android 4.4.4; zh-cn; HTC D820u Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko)Version/4.0 MQQBrowser/5.6 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; U; Android 4.4.4; zh-CN; HTC D820u Build/KTU84P) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 UCBrowser/10.1.0.527 U3/0.8.0 Mobile Safari/534.30",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) CriOS/40.0.2214.69 Mobile/12A365 Safari/600.1.4",
            "Mozilla/5.0 (Linux; U; Android 4.4.4; zh-CN; HTC D820u Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Oupeng/10.2.3.88150 Mobile Safari/537.36",
        ]

    def process_request(self, request, spider):
        if not request.headers.get('User-Agent'):
            request.headers['User-Agent'] = random.choice(self.user_agents)


class DownImgloadPipeline(ImagesPipeline):
    """docstring for DoubanDownloadPipeline"""

    def get_media_requests(self, item, info):
        default_headers = {
            'accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Host': 'img5.imgtn.bdimg.com',
            'referer': item['refere'],
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36'
        }
        yield scrapy.Request(item['url'],headers=default_headers,meta={"item":item})


    def file_path(self, request, response=None, info=None):
        item = request.meta["item"]
        # 再从item中取出分类名称,这个name就是我们想自定义图片路径的文件名称,(如果不自定义file_path函数的话,默认会将图片下载到full文件里)
        name = item['path']
        # 再从item中取出img_url,分隔出来图片的名称.图片的网址一般最后一个'/'后都是数字,此处用它作图片的名字
        img_url_name = item['name']+'.jpg'
        return "%s/%s" % (name, img_url_name)
        # print(request)

    def item_completed(self, results, item, info):
        pass


class ProxyMiddleware(object):
    '''
    代理ip中间件
    '''
    # 参考scrapy retry中间件源码
    EXCEPTIONS_TO_RETRY = (defer.TimeoutError, TimeoutError, DNSLookupError,
                           ConnectionRefusedError, ConnectionDone, ConnectError,
                           ConnectionLost, TCPTimedOutError, ResponseFailed,
                           IOError, TunnelError)

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.proxies_list = []
        self.request_per_domain = ''

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def spider_opened(self, spider):
        # 并发值
        self.request_per_domain = spider.custom_settings.get(
            'CONCURRENT_REQUESTS_PER_IP') or spider.custom_settings.get('CONCURRENT_REQUESTS_PER_DOMAIN')
        spider.logger.info("爬虫:{} 并发值是:{}".format(spider.name, self.request_per_domain))

    def process_request(self, request, spider):
        if request.meta.get('no_proxy'):  # 个别请求不使用代理
            spider.logger.info(f'请求不使用代理: {request.url}')
        else:
            check_proxy_url = spider.check_proxy_url if hasattr(spider, 'check_proxy_url') else request.url
            one_proxy_dict = get_one_proxy(self.proxies_list, check_proxy_url)
            if not one_proxy_dict:
                self.proxies_list = get_valid_proxy_pool(
                    check_proxy_url=check_proxy_url,
                    request_per_domain=self.request_per_domain)
                one_proxy_dict = get_one_proxy(self.proxies_list, check_proxy_url)
            proxy_meta = "{}:{}".format(one_proxy_dict['ip'], one_proxy_dict['port'])

            if request.url.startswith("https"):
                self.logger.debug(
                    '爬虫:{} 使用ProxyMiddleware代理:{},请求:{}'.format(spider.name, "https://" + proxy_meta, request.url))
                request.meta["proxy"] = "https://" + proxy_meta
            else:
                self.logger.debug(
                    '爬虫:{} 使用ProxyMiddleware代理:{} ,请求:{}'.format(spider.name, "http://" + proxy_meta, request.url))
                request.meta["proxy"] = "http://" + proxy_meta

    def process_response(self, request, response, spider):
        if response.status in [403, 400] and 'proxy' in request.meta:
            # 当请求出现异常的时候, 代理池哪些代理IP在本域名下是不可以用的
            proxy = request.meta['proxy']
            self.logger.info("代理不可用,丢弃。代理:{},域名:{}".format(proxy, request.url))
            proxy_ip = re.findall('https?://(.+?):\d+', proxy)[0]
            for proxy_dict in self.proxies_list:
                if proxy_ip in proxy_dict['ip']:
                    # 获取索引
                    _index = self.proxies_list.index(proxy_dict)
                    # 丢弃
                    self.proxies_list.pop(_index)
            return request
        return response

    def process_exception(self, request, exception, spider):
        if isinstance(exception, self.EXCEPTIONS_TO_RETRY):
            # 当请求出现异常的时候, 代理池哪些代理IP在本域名下是不可以用的
            proxy = request.meta['proxy']
            self.logger.info("代理不可用,丢弃。代理:{},域名:{}".format(proxy, request.url))
            proxy_ip = re.findall('https?://(.+?):\d+', proxy)[0]
            for proxy_dict in self.proxies_list:
                if proxy_ip in proxy_dict['ip']:
                    # 获取索引
                    _index = self.proxies_list.index(proxy_dict)
                    # 丢弃
                    self.proxies_list.pop(_index)
        return request