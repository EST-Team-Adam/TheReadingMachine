# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


import pandas as pd
from scrapy.exceptions import DropItem
from datetime import datetime
import thereadingmachine.environment as env


class DuplicatesPipeline(object):

    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        if item['link'] in self.ids_seen:
            raise DropItem('Duplicate item found: %s' % item)
        else:
            self.ids_seen.add(item['link'])
            return item


class SanitizeArticlePipeline(object):

    def _sanitize_article(self, article):
        sanitized_article = (
            article
            .replace('\r', ' ')
            .replace('\n', ' ')
            .replace('\\r', ' ')
            .replace('\\n', ' ')
            .replace('\t', ' ')
            .replace('\\"', '')
            .replace('"', ''))

        return sanitized_article

    def process_item(self, item, spider):
        item['title'] = item['title'].encode('utf-8', 'ignore')
        if item['title'] in ('News – EURACTIV.com', '\r\n\tWorld Grain\r\n'):
            raise DropItem('Invalid Item in %s' % item)
        if 'article' in dict(item):
            sanitized_article = self._sanitize_article(
                ' '.join(item['article']))
            try:
                sanitized_article = sanitized_article.encode('utf-8', 'ignore')
            except UnicodeDecodeError:
                sanitized_article = sanitized_article.decode(
                    'unicode_escape').encode('utf-8', 'ignore')
            item['article'] = sanitized_article
        if len(item['date']) == 0:
            raise DropItem('Empty Date in %s' % item)
        elif len(item['article']) > 0:
            return item
        else:
            raise DropItem('Empty Article in %s' % item)


class AmisScrapePipeline(object):

    def __init__(self):
        self.data_list = []
        self.today = datetime.today()

    def open_spider(self, spider):
        pass

    def process_item(self, item, spider):
        try:
            item_dict = dict(item)
            item_dict['source'] = spider.name
            self.data_list.append(item_dict)
        except (UnicodeDecodeError, UnicodeEncodeError):
            raise DropItem('Formatting Error in %s' % item)
        return item

    def close_spider(self, spider):
        scraped_data = pd.DataFrame(self.data_list)
        scraped_data['article'] = scraped_data['article'].apply(
            lambda x: x.decode('utf-8'))
        scraped_data['title'] = scraped_data['title'].apply(
            lambda x: x.decode('utf-8'))
        scraped_data['date'] = pd.to_datetime(scraped_data['date'])
        scraped_data.to_sql(con=env.engine,
                            name=env.raw_article_table,
                            index=False,
                            if_exists='append',
                            dtype=env.raw_article_field_type)
