import scrapy
import re
import w3lib.html as w3


class LighttpdSpider(scrapy.Spider):
    name = 'lighttpd'
    #start_urls = ['http://localhost:8000']
    start_urls = ["https://www.mpbhba.org/business-resources/"]

    def parse(self, response):

        base = response.css('body')
        one  = base.xpath("//p").getall()
       
        print(base)
        for item in one:
            print(item, '\n')

#        for item in lis:
#             print(self._parse_something(item))
#
#        print('!!!!')
#
#    def _parse_something(self, item):
#         return(w3.remove_tags(item))

'''
output= w3lib.html.remove_tags(input)
print(output)
'''

#lis = response.xpath("//li/text()").getall()
#lis = response.xpath("//li[contains(text(), 'files')]/following-sibling::li/text()").getall()

#for p_node in response.xpath('//h3[contains(., 'General Meetings')]/following-sibling::p[position() < last()]'):
#    address = p_node.xpath('./text()[last()]).get()
#    date = p_node.xpath('./text()[last() - 1]).get()
