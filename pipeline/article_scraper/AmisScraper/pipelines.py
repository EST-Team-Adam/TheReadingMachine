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


DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'resources'))


class DuplicatesPipeline(object):

    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        if item['link'] in self.ids_seen:
            spider.logf.write("Duplicate item found: %s\n" % item)
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.ids_seen.add(item['link'])
            return item


class SanitizeArticlePipeline(object):
    def __init__(self):
        stf = open(DATA_DIR+'/stop_words.txt', 'r')
        stop_words = [line.strip() for line in stf]
        self.stop_words = set(stop_words)

    def _check_stop_words(self, word):
        word = word.strip()
        return len(word) > 2 and word not in self.stop_words

    def process_item(self, item, spider):
        if 'article' in dict(item):
            sanitized_article = " ".join([x for x in item['article'] if self._check_stop_words(x)])
            sanitized_article = sanitized_article.replace('\n', '').replace('\t', ' ')
            item['article'] = sanitized_article.encode('ascii', 'ignore')
        if len(item['date']) == 0:
            spider.logf.write("Empty Date in %s\n" % item)
            raise DropItem("Empty Date in %s" % item)
        elif len(item['article']) > 0:
            return item
        else:
            spider.logf.write("Empty Article in %s\n" % item)
            raise DropItem("Empty Article in %s" % item)


class AmisJsonPipeline(object):
    lock = threading.Lock()
    datafile = open('blog_articles_{0}.jsonl'.format(time.strftime("%d_%m_%Y")), 'a')

    def __init__(self):
        pass

    def process_item(self, item, spider):
        item_dict = dict(item)
        item_dict['source'] = spider.name
        line = json.dumps(item_dict) + "\n"
        AmisJsonPipeline.lock.acquire()
        AmisJsonPipeline.datafile.write(line)
        AmisJsonPipeline.lock.release()
        return item
