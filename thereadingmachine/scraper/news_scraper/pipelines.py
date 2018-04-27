# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


import os
import json
import threading
from scrapy.exceptions import DropItem
from datetime import datetime

data_dir = os.environ['DATA_DIR']
scraper_file_prefix = os.environ['SCRAPER_FILE_PREFIX']
scraper_output_path = os.path.join(data_dir, 'scraper_output')

if not os.path.exists(scraper_output_path):
    os.makedirs(scraper_output_path)


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


class AmisJsonPipeline(object):

    def __init__(self):
        self.datafiles = {}
        self.today = datetime.today()

    def open_spider(self, spider):
        if spider.name not in self.datafiles.keys():
            target_file_name = '{}_{}_{}.jsonl'.format(
                scraper_file_prefix, self.today.strftime('%Y_%m_%d'), spider.name)
            target_file_path = os.path.join(
                scraper_output_path, target_file_name)
            self.datafiles[spider.name] = open(target_file_path, 'a')
        self.lock = threading.Lock()

    def process_item(self, item, spider):
        # spider.logger.info('Processing Item: ' + item['title'])
        self.lock.acquire()
        try:
            item_dict = dict(item)
            item_dict['source'] = spider.name
            line = json.dumps(item_dict, ensure_ascii=False) + '\n'
            self.datafiles[spider.name].write(line)
            # spider.logger.info('Written Item: ' + item['title'])
        except (UnicodeDecodeError, UnicodeEncodeError):
            raise DropItem('Formatting Error in %s' % item)
        self.lock.release()
        return item

    def close_spider(self, spider):
        for datafile in self.datafiles.values():
            datafile.close()
