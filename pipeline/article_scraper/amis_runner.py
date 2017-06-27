from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# you can run scrapers in two ways:
# scrapy crawl <spider name>
# (to run a specific spider)
# python amis_runner.py
# (to run all the spiders)

process = CrawlerProcess(get_project_settings())

spiders = ['bloomberg', 'noggers', 'worldgrain', 'euractiv', 'agrimoney']

for spider in spiders:
    process.crawl(spider)

process.start()
