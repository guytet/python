import scrapy
import re


class LighttpdSpider(scrapy.Spider):
    name = 'lighttpd'
    allowed_domains = ['localhost']
    start_urls = ['http://localhost/']

    def parse(self, response):
        allitems = response.xpath("//li").getall()
        for item in allitems:
            print(self._parse_something(item))


    def _parse_something(self, someline):
        try: 
            if re.search('weekly', someline):
                return True 
        except:
            pass

'''
//button[contains(text(),"Go")] 
'''
