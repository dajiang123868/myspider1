# -*- coding: utf-8 -*-
import scrapy
from scrapy_splash import SplashRequest

script = """
function main(splash, args)
  splash.images_enabled = false
  splash:set_user_agent("{ua}")
  assert(splash:go(args.url))
  local scroll_to = splash:jsfunc("window.scrollTo")
  scroll_to(0, 2000)
  assert(splash:wait(args.wait))
  return splash:html()
end""".format(
    ua="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36")


class UniversalSpiderSplashSpider(scrapy.Spider):
    name = 'universal_spider_splash'
    allowed_domains = ['quote.eastmoney.com']
    start_urls = ['http://quote.eastmoney.com/sh603662.html']
    custom_settings = {
        # 'RANDOMIZE_DOWNLOAD_DELAY': True,
        # 'DOWNLOAD_DELAY': 60 / 60.0,
        # 'CONCURRENT_REQUESTS_PER_IP': 16,
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy_splash.SplashCookiesMiddleware': 723,
            'scrapy_splash.SplashMiddleware': 725,
            'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
            # 'main_spider.middlewares.SplashProxyMiddleware': 843,  # 代理ip,此方法没成功
            # 'main_spider.middlewares.RandomUserAgentMiddleware': 843,
        },
        # 入库
        'ITEM_PIPELINES': {
            # 'main_spider.pipelines.MysqlPipeline': 402,
            # 'main_spider.pipelines.RiskControlInfoPipeline': 401,
        },
        'SPIDER_MIDDLEWARES': {
            # 'main_spider.middlewares.RiskControlInfoSpiderMiddleware': 543,
            'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
        },
    }

    def __init__(self, **kwargs):
        super(UniversalSpiderSplashSpider, self).__init__()
        self.target_urls = [
            "http://quote.eastmoney.com/sh603662.html",
        ]

    def start_requests(self):
        for request_url in self.target_urls:
            yield SplashRequest(url=request_url,
                                meta={"request_url": request_url},
                                callback=self.parse,
                                endpoint='execute',
                                args={
                                    'lua_source': script,
                                    'wait': 8})

    def parse(self, response):
        nodes1 = response.xpath('//*[@id="quote-digest"]//tr/td/text()')
        pass
