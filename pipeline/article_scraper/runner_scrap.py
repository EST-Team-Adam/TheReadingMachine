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

#process.start()

spiders = [ 'noggers', 'worldgrain', 'euractiv', 'agrimoney']

for spider in spiders:
    process.crawl(spider)

process.start()



flattened_article_df = pd.DataFrame()
for spider in spiders:
  json_file = data_dir + '/blog_articles_{0}_{1}.jsonl'.format(time.strftime("%d_%m_%Y"), spider)
  if os.path.isfile(json_file):
      flattened_article_df = flattened_article_df.append(pd.read_json(json_file, lines=True), ignore_index=True)
flattened_article_df.date = flattened_article_df.date.apply(lambda d: datetime.strptime(str(d), '%Y-%m-%d %H:%M:%S'))

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
