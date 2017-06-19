# -*- coding: utf-8 -*-

# Scrapy settings for amisSpider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'AmisScraper'

SPIDER_MODULES = ['AmisScraper.spiders']
NEWSPIDER_MODULE = 'AmisScraper.spiders'


#LOG_STDOUT = True
#LOG_FILE = 'scrapy_output.log'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'amisSpider (+http://www.yourdomain.com)'

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY=3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN=16
#CONCURRENT_REQUESTS_PER_IP=16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False


# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'AmisScraper.pipelines.DuplicatesPipeline': 100,
    'AmisScraper.pipelines.SanitizeArticlePipeline': 300,
    'AmisScraper.pipelines.AmisJsonPipeline': 500
}
