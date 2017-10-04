import os
import time
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


# Configuration
data_dir = os.environ['DATA_DIR']
target_data_table = 'RawArticle'
engine = create_engine('sqlite:///{0}/the_reading_machine.db'.format(data_dir))
scraper_file_prefix = os.environ['SCRAPER_FILE_PREFIX']

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


def save_json_to_db(spiders, date_col='date'):
    ''' Function to load the scraped article and save it back to the database.
    '''

    flattened_article_df = pd.DataFrame()

    for spider in spiders:
        current_file_name = '{}_{}_{}.jsonl'.format(
            scraper_file_prefix, time.strftime("%d_%m_%Y"), spider)
        current_file_path = os.path.join(data_dir, current_file_name)
        print(current_file_path)

        if os.path.isfile(current_file_path):
            current_source = pd.read_json(current_file_path, lines=True)
            flattened_article_df = (
                flattened_article_df
                .append(current_source, ignore_index=True))
        else:
            raise TypeError(
                'source file for spider "{}" does not exist'.format(spider))

    flattened_article_df.to_sql(con=engine,
                                name=target_data_table,
                                index=False,
                                if_exists='replace',
                                dtype=field_type)
