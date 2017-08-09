import pandas as pd
import os
import time
import shutil
import sqlalchemy
from sqlalchemy import create_engine
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# Configuration
os.environ['DATA_DIR'] = '/Users/luca_pozzi/Documents/GitHub/TheReadingMachine/data'
os.environ['SCRAPY_CONFIG_DIR'] = '~/Documents/GitHub/TheReadingMachine/pipeline/article_scraper'
spider = 'bloomberg'
#spider = 'worldgrain'

data_dir = os.environ['DATA_DIR']
cfg_dir = os.environ['SCRAPY_CONFIG_DIR']
cfg_file = cfg_dir + '/scrapy.cfg'
local_directory = os.getcwd()

process = CrawlerProcess(get_project_settings())
process.crawl(spider)

process.start()


#www.bloomberg.com/news/audio/2016-11-02/jim-bianco-on-yield-curve-next-big-move-in-rates-will-be-lower