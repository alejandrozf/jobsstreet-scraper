# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JobStreetItem(scrapy.Item):
    # define the fields for your item here like:
    company_name = scrapy.Field()
    e_mail = scrapy.Field()
    phone_number = scrapy.Field()
