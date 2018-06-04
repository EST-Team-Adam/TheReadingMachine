import os
import pandas as pd
import sqlalchemy
from datetime import datetime
from datetime import timedelta
from sqlalchemy import create_engine
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


# Configuration
target_data_table = 'RawArticle'
engine = create_engine('sqlite:///{0}/the_reading_machine.db'.format(data_dir))

field_type = {'source': sqlalchemy.types.Unicode(length=255),
              'title': sqlalchemy.types.Unicode(length=255),
              'date': sqlalchemy.types.Date(),
              'link': sqlalchemy.types.Unicode(length=255),
              'article': sqlalchemy.types.UnicodeText}


def scrap_articles(spiders):
    ''' Function to start the scrapers.
    '''

    process = CrawlerProcess(get_project_settings())
    for spider in spiders:
        process.crawl(spider)

    process.start()
