# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsArticleItem(scrapy.Item):
    title = scrapy.Field()
    date = scrapy.Field()
    link = scrapy.Field()
    article = scrapy.Field()
    pass
