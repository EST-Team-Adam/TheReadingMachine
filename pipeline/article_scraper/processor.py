import pandas as pd
import os
import time
from shutil import copy2
import sqlalchemy
from sqlalchemy import create_engine
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# Configuration
data_dir = os.environ['DATA_DIR']
cfg_dir = os.environ['SCRAPY_CONFIG_DIR']
cfg_file = cfg_dir + '/scrapy.cfg'

target_data_table = 'RawArticle'
engine = create_engine('sqlite:///{0}/the_reading_machine.db'.format(data_dir))

# Copy cfg file in the current directory
copy2(cfg_file, os.getcwd())

process = CrawlerProcess(get_project_settings())

spiders = ['bloomberg', 'noggers', 'worldgrain', 'euractiv', 'agrimoney']

for spider in spiders:
    process.crawl(spider)

process.start()

json_file = data_dir + '/blog_articles_{0}.jsonl'.format(
    time.strftime("%d_%m_%Y"))
if os.path.isfile(json_file):
    flattened_article_df = pd.read_json(json_file, lines=True)

# Save output file
field_type = {'source': sqlalchemy.types.Unicode,
              'title': sqlalchemy.types.Unicode,
              'date': sqlalchemy.types.NVARCHAR(length=255),
              'link': sqlalchemy.types.Unicode,
              'article': sqlalchemy.types.Unicode,
              'source': sqlalchemy.types.Unicode
              }

flattened_article_df.to_sql(con=engine, name=target_data_table, index=False,
                            if_exists='replace',
                            dtype=field_type)
