import pandas as pd
import os
import time
import shutil
import sqlalchemy
from sqlalchemy import create_engine
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# Configuration
data_dir = os.environ['DATA_DIR']
cfg_dir = os.environ['SCRAPY_CONFIG_DIR']
cfg_file = cfg_dir + '/scrapy.cfg'
local_directory = os.getcwd()

target_data_table = 'RawArticle'
engine = create_engine('sqlite:///{0}/the_reading_machine.db'.format(data_dir))

# Copy cfg file in the current directory
if not os.path.isfile(local_directory + '/scrapy.cfg'):
    shutil.copy2(cfg_file, local_directory)

# Create logs folder
log_dir = local_directory + '/logs'
if os.path.exists(log_dir):
    shutil.rmtree(log_dir)
os.makedirs(log_dir)

process = CrawlerProcess(get_project_settings())

spiders = ['bloomberg', 'noggers', 'worldgrain', 'euractiv', 'agrimoney']

for spider in spiders:
    process.crawl(spider)

process.start()

flattened_article_df = pd.DataFrame()
for spider in spiders:
  json_file = data_dir + '/blog_articles_{0}_{1}.jsonl'.format(
    time.strftime("%d_%m_%Y"), spider)
  if os.path.isfile(json_file):
    flattened_article_df = flattened_article_df.append(pd.read_json(json_file, lines=True), ignore_index=True)

# Save output file
field_type = {'source': sqlalchemy.types.Unicode(length=255),
              'title': sqlalchemy.types.Unicode(length=255),
              'date': sqlalchemy.types.NVARCHAR(length=255),
              'link': sqlalchemy.types.Unicode(length=255),
              'article': sqlalchemy.types.UnicodeText
              }

flattened_article_df.to_sql(con=engine, name=target_data_table, index=False,
                            if_exists='replace',
                            dtype=field_type)
