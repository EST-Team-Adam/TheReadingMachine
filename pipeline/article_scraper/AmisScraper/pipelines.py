# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import os
from scrapy.exceptions import DropItem
import threading
import time

data_dir = os.environ['DATA_DIR']


class DuplicatesPipeline(object):

    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        if item['link'] in self.ids_seen:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.ids_seen.add(item['link'])
            return item


class SanitizeArticlePipeline(object):

    def __init__(self):
        stf = open(data_dir + '/stop_words.txt', 'r')
        stop_words = [line.strip() for line in stf]
        self.stop_words = set(stop_words)

    def _check_stop_words(self, word):
        word = word.strip()
        return len(word) > 2 and word not in self.stop_words

    def _sanitize_article(self, article):
        return(article.replace('\r', ' ').replace('\n', ' ')
               .replace('\\r', ' ').replace('\\n', ' ')
               .replace('\t', ' ').replace('\\"', '').replace('"', ''))

    def process_item(self, item, spider):
        item['title'] = item['title'].encode('utf-8', 'ignore')
        if item['title'] in ('News – EURACTIV.com', '\r\n\tWorld Grain\r\n'):
            raise DropItem("Invalid Item in %s" % item)
        if 'article' in dict(item):
            sanitized_article = " ".join(
                [x for x in item['article'] if self._check_stop_words(x)])
            sanitized_article = self._sanitize_article(sanitized_article)
            try:
                sanitized_article = sanitized_article.encode('utf-8', 'ignore')
            except UnicodeDecodeError:
                sanitized_article = sanitized_article.decode(
                    'unicode_escape').encode('utf-8', 'ignore')
            item['article'] = sanitized_article
        if len(item['date']) == 0:
            raise DropItem("Empty Date in %s" % item)
        elif len(item['article']) > 0:
            return item
        else:
            raise DropItem("Empty Article in %s" % item)


class AmisJsonPipeline(object):

    def __init__(self):
        self.datafiles = {}

    def open_spider(self, spider):
        if spider.name not in self.datafiles.keys():
            self.datafiles[spider.name] = open(data_dir + '/blog_articles_{0}_{1}.jsonl'.format(
                time.strftime("%d_%m_%Y"), spider.name), 'a')  # , 0)
        self.lock = threading.Lock()

    def process_item(self, item, spider):
        # spider.logger.info("Processing Item: " + item['title'])
        self.lock.acquire()
        try:
            item_dict = dict(item)
            item_dict['source'] = spider.name
            line = json.dumps(item_dict, ensure_ascii=False) + "\n"
            self.datafiles[spider.name].write(line)
            # spider.logger.info("Written Item: " + item['title'])
        except (UnicodeDecodeError, UnicodeEncodeError):
            raise DropItem("Formatting Error in %s" % item)
        self.lock.release()
        return item

    def close_spider(self, spider):
        for datafile in self.datafiles.values():
            datafile.close()
