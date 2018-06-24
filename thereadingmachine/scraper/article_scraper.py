from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


def scrap_articles(spiders):
    ''' Function to start the scrapers.
    '''

    process = CrawlerProcess(get_project_settings())
    for spider in spiders:
        process.crawl(spider)

    process.start()
