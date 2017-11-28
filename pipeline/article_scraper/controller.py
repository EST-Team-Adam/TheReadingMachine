import os
import pandas as pd
import sqlalchemy
from datetime import datetime
from datetime import timedelta
from sqlalchemy import create_engine
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


# Configuration
data_dir = os.environ['DATA_DIR']
target_data_table = 'RawArticle'
engine = create_engine('sqlite:///{0}/the_reading_machine.db'.format(data_dir))
scraper_file_prefix = os.environ['SCRAPER_FILE_PREFIX']
scraper_output_path = os.path.join(data_dir, 'scraper_output')

if not os.path.exists(scraper_output_path):
    os.makedirs(scraper_output_path)


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
    today = datetime.today()
    for spider in spiders:
        current_file_name = '{}_{}_{}.jsonl'.format(
            scraper_file_prefix, today.strftime('%Y_%m_%d'), spider)
        current_file_path = os.path.join(
            scraper_output_path, current_file_name)

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

    # Delete old files
    #
    # We delete files from two days ago, so that we still have data scraped
    # yester for recover.
    two_days_ago = today - timedelta(days=2)
    old_file_name = '{}_{}_{}.jsonl'.format(
        scraper_file_prefix, two_days_ago.strftime('%Y_%m_%d'), spider)
    old_file_path = os.path.join(
        scraper_output_path, old_file_name)
    if os.path.isfile(old_file_path):
        os.remove(old_file_path)
