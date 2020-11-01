import scrapy


class LighttpdSpider(scrapy.Spider):
    name = 'lighttpd'
    allowed_domains = ['172.17.0.2']
    start_urls = ['http://172.17.0.2/']

    def parse(self, response):
        pass
