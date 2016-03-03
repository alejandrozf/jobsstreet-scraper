import re
#~ import os

import uuid
import string

#~ import ipdb

from email.utils import parseaddr
from pprint import pprint
import scrapy

INDONESIA = {'allowed_domains': "jobstreet.co.id",
			 'start_urls':"http://www.jobstreet.co.id/en/job-search/job-vacancy.php"}
			 
VIETNAM = {'allowed_domains': "jobstreet.vn",
			'start_urls':"http://www.jobstreet.vn/vi/job-search/job-vacancy.php"}
			
PHILIPPINES	= {'allowed_domains': "jobstreet.com.ph",
				'start_urls':"http://www.jobstreet.com.ph/en/job-search/job-vacancy.php"}

spaces = re.compile(r'\s|"')


from jobstreet.items import JobStreetItem

class JobStreetSpider(scrapy.Spider):
    name = "jobstreet"
    country = 'my'
    allowed_domains = [INDONESIA['allowed_domains']]
    start_urls = [INDONESIA['start_urls']]
    
    #~ max_pages = 987         # number of pages to follow(site max is 987) ~8 per day & 20 per page 
    max_pages = 3		         # number of pages to follow(site max is 987) ~8 per day & 20 per page 
    date  = 2               # upto x days posted
    counter = 1             # pages scraped
    
    current_company_name = []
    
    def save_page(self,folder,response):
        with open(folder+str(uuid.uuid4())+'.html','w') as f:
            f.write(response.body)    
      
    def parse_link_contents(self,response):
        item = JobStreetItem()
        item['e_mail'] = self.search_email(response)
        item['phone_number'] = self.search_phone_number(response)
        item['company_name'] = self.search_company(response)
        if item['company_name'] == []:
            #~ ipdb.set_trace()
            self.save_page('./no_company/',response)
        #~ if item['company_name'] and item['e_mail'] and item['phone_number']:
        if item['company_name'] and (item['e_mail'] or item['phone_number']):
            yield item
    
    def search_company(self,response):
        
        def format_response(res):
            if res:
                try:
                    return spaces.sub('',res)
                except TypeError:
                    #~ ipdb.set_trace()
                    return spaces.sub('',res[0])
            return res
        
        res = self.current_company_name
        if not res:
            res = response.xpath(".//*[@id='company_name']/a/text()").extract()
        if not res:
            res = response.xpath(".//*[@id='company_name']/div/text()").extract()
        if not res:
            res = response.xpath(".//*[@itemprop='hiringOrganization']/a/text()").extract()
        if not res:
            res = response.xpath(".//*[@itemprop='hiringOrganization']/div/text()").extract()
        if not res:
            res = response.xpath(".//*[@itemprop='hiringOrganization']/text()").extract()
        if not res:
            res = response.xpath(".//*[@id='company_name']/text()").extract()
        if not res:
            res = response.xpath(".//*[@class='rRowCompanyCls']/text()").extract()
        if not res:
            #~ ipdb.set_trace()
            res = response.xpath(".//center/text()").extract()
        if not res:
            #~ ipdb.set_trace()
            res = response.xpath(".//b/text()").extract()
        return format_response(res) 
        
    
    def search_email(self,response):
        #~ return response.xpath('//body').re_first(r'[\w.-]+@[\w.-]+.\w+')
        return response.xpath('//body').re_first("([a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\/=?^_`"
                    "{|}~-]+)*(@|\sat\s)(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?(\.|"
                    "\sdot\s))+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)")
    
    def search_phone_number(self,response):
        val = response.xpath(".//*[@itemprop='telephone']/text()").extract()
        if not val:
            val = response.xpath('//body').re(r'''
                                                            # don't match beginning of string, number can start anywhere
                                                (\d{3})     # area code is 3 digits (e.g. '800')
                                                \D*         # optional separator is any number of non-digits
                                                (\d{3})     # trunk is 3 digits (e.g. '555')
                                                \D*         # optional separator
                                                (\d{4})     # rest of number is 4 digits (e.g. '1212')
                                                \D*         # optional separator
                                                (\d*)       # extension is optional and can be any number of digits
                                                $           # end of string
                                                ''')
        return val
                
    def parse(self, response):
        if self.counter < self.max_pages:
            #retrieving links
            for href in response.xpath(".//*[@class='position-title-link']"):
                url = href.xpath('.//@href').extract()[0]
                #~ print url,'\n'
                self.current_company_name = href.xpath("../../*[@class='company-name']/@href").extract()
                yield scrapy.Request(url, callback=self.parse_link_contents)
            self.counter += 1
            url = response.xpath(".//*[@id='page_next']/@href")[0].extract()
            pprint(url)
            #~ print '\n'
            yield scrapy.Request(url,callback=self.parse)
