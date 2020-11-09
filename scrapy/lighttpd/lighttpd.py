import scrapy
import re
import w3lib.html


class LighttpdSpider(scrapy.Spider):
    name = 'lighttpd'
    allowed_domains = ['localhost']
    start_urls = ['http://localhost/']

    def parse(self, response):

        print('!!!!')

        lis = response.xpath("//li[contains(text(), 'files')]/following-sibling::*").getall()
        for item in lis:
             print(self._parse_something(item))

        print('!!!!')

    def _parse_something(self, item):
         return(w3lib.html.remove_tags(item))

'''
output= w3lib.html.remove_tags(input)
print(output)
'''

#lis = response.xpath("//li/text()").getall()
#lis = response.xpath("//li[contains(text(), 'files')]/following-sibling::li/text()").getall()

#for p_node in response.xpath('//h3[contains(., 'General Meetings')]/following-sibling::p[position() < last()]'):
#    address = p_node.xpath('./text()[last()]).get()
#    date = p_node.xpath('./text()[last() - 1]).get()
