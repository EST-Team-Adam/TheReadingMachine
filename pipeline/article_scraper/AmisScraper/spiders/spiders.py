from AmisScraper.items import NewsArticleItem
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from datetime import datetime
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.utils.response import get_base_url



class UnicodeFriendlyLinkExtractor(SgmlLinkExtractor):
    """
    Need this to fix the encoding error.
    Taken from https://stackoverflow.com/questions/17862016/scrapy-python-unicode-links-error
    """
    def extract_links(self, response):
        base_url = None
        if self.restrict_xpaths:
            hxs = HtmlXPathSelector(response)
            base_url = get_base_url(response)
            body = u''.join(f for x in self.restrict_xpaths
                           for f in hxs.select(x).extract())
            try:
                body = body.encode(response.encoding)
            except UnicodeEncodeError:
                body = body.encode('utf-8')
        else:
            body = response.body

        links = self._extract_links(body, response.url, response.encoding, base_url)
        links = self._process_links(links)
        return links



class BloombergSpider(CrawlSpider):
    name = "bloomberg"
    # logf = open("logs/bloomberg.log", "w")
    allowed_domains = ["bloomberg.com"]
    start_urls = ["http://www.bloomberg.com"]
    rules = [
        Rule(UnicodeFriendlyLinkExtractor(allow='(/news/articles/)((?!:).)*$'),
             callback="parse_item", follow=True),
        Rule(UnicodeFriendlyLinkExtractor(allow='(/news/)((?!:).)*$'),
             callback="parse_item", follow=True),
        Rule(UnicodeFriendlyLinkExtractor(allow='(/articles/)((?!:).)*$'),
             callback="parse_item", follow=True)
    ]

    def parse_item(self, response):
        item = NewsArticleItem()
        title = response.xpath('//title/text()')[0].extract()
        article = response.xpath('//p/text()').extract()
        self.logger.info("Scraping Title: " + title)
        try:
            item['title'] = title
            item['article'] = article
            item['link'] = response.url.replace('http://', '').replace('https://', '')
            raw_date = response.url.split("/")[-2]
            date = datetime.strptime(raw_date, '%Y-%m-%d')
            item['date'] = str(date)
            return item
        except Exception as e:
            pass
            # self.logf.write("Failed to scrape {0}: {1}\n".format(str(response.url), str(e)))


class NoggersBlogSpider(CrawlSpider):
    name = "noggers"
    # logf = open("logs/noggers.log", "w")
    allowed_domains = ["nogger-noggersblog.blogspot.it"]
    start_urls = ["http://nogger-noggersblog.blogspot.it/"]
    rules = [
        Rule(UnicodeFriendlyLinkExtractor(allow='((?!:).)*html$'),
             callback="parse_item", follow=True)
    ]

    def parse_item(self, response):
        item = NewsArticleItem()
        title = response.xpath('//a/text()')[8].extract()
        article = response.xpath('//div/text()').extract()
        self.logger.info("Scraping Title: " + title)
        item['title'] = title
        item['article'] = article
        item['link'] = response.url.replace('http://', '').replace('https://', '')
        try:
            token = filter(lambda x: '--' in x, article)
            try:
                raw_date = token[0].split(' -- ')[0].replace('\n', '')
                date = datetime.strptime(raw_date, '%d/%M/%y')
            except (ValueError, IndexError):
                try:
                    raw_date = title.split("Nogger's Blog: ")[1]
                    date = datetime.strptime(raw_date, '%d-%b-%Y')
                except (ValueError, IndexError):
                    date = ""
            item['date'] = str(date)
            return item
        except Exception as e:
            pass
            # self.logf.write("Failed to scrape {0}: {1}\n".format(str(response.url), str(e)))


class WorldGrainSpider(CrawlSpider):
    name = "worldgrain"
    # logf = open("logs/worldgrain.log", "w")
    allowed_domains = ["world-grain.com"]
    start_urls = ["http://www.world-grain.com"] + \
                 ["http://www.world-grain.com/News/Archive.aspx?page={0}&year={1}&month=0".format(i, j)
                  for i in range(1, 50) for j in range(2006, 2017)]
    rules = [
        Rule(UnicodeFriendlyLinkExtractor(allow='(/articles/news_home/)((?!:).)*$'),
             callback="parse_item", follow=True),
        Rule(UnicodeFriendlyLinkExtractor(allow='(/news_home/)((?!:).)*$'),
             callback="parse_item", follow=True),
        Rule(UnicodeFriendlyLinkExtractor(allow='(/articles/)((?!:).)*$'),
             callback="parse_item", follow=True)
    ]

    def parse_item(self, response):
        item = NewsArticleItem()
        title = response.xpath('//title/text()')[0].extract()
        article = response.xpath('//p/text()').extract() + \
            response.xpath('//br/text()').extract()
        self.logger.info("Scraping Title: " + title)
        item['title'] = title
        item['article'] = article
        item['link'] = response.url.replace('http://', '').replace('https://', '')

        try:
            raw_date = "{0}-{1}".format(response.url.split("/")
                                        [-2], response.url.split("/")[-3])
            date = datetime.strptime(raw_date, '%m-%Y')
            item['date'] = str(date)
            return item
        except Exception as e:
            pass
            # self.logf.write("Failed to scrape {0}: {1}\n".format(str(response.url), str(e)))


class EuractivSpider(CrawlSpider):
    name = "euractiv"
    # logf = open("logs/euractiv.log", "w")
    allowed_domains = ["www.euractiv.com"]
    start_urls = ["http://www.euractiv.com"]
    rules = [
        Rule(UnicodeFriendlyLinkExtractor(allow='(/agriculture-food/news/)((?!:).)*$'),
             callback="parse_item", follow=True),
        Rule(UnicodeFriendlyLinkExtractor(allow='(/news/)((?!:).)*$'),
             callback="parse_item", follow=True)
    ]

    def parse_item(self, response):
        item = NewsArticleItem()
        try:
            title = response.xpath('//title/text()')[0].extract()
            article = response.xpath('//p/text()').extract()
            item['title'] = title
            item['article'] = article
            item['link'] = response.url.replace('http://', '').replace('https://', '')
        except UnicodeDecodeError:
                pass
        self.logger.info("Scraping Title: " + title)
        
        try:
            raw_date = response.xpath(
                '//*[contains(@class,"ea-dateformat")]/text()').extract()[1].strip()
            date = datetime.strptime(raw_date, '%d-%m-%Y')
            item['date'] = str(date)
            return item
        except Exception as e:
            pass
            # self.logf.write("Failed to scrape {0}: {1}\n".format(str(response.url), str(e)))


class AgriMoneySpider(CrawlSpider):
    name = "agrimoney"
    # logf = open("logs/agrimoney.log", "w")
    allowed_domains = ["www.agrimoney.com"]
    start_urls = [
        "http://www.agrimoney.com",
        "http://www.agrimoney.com/search/",
        "http://www.agrimoney.com/searchdate/"
    ] + ["http://www.agrimoney.com/search/{0}/".format(i) for i in range(600)] + \
        ["http://www.agrimoney.com/searchdate/{0}/".format(i)
         for i in range(500)]
    rules = [
        Rule(UnicodeFriendlyLinkExtractor(allow='(/news/)((?!:).)*html$'),
             callback="parse_item", follow=True),
        Rule(UnicodeFriendlyLinkExtractor(allow='(/feature/)((?!:).)*html$'),
             callback="parse_item", follow=True),
        Rule(UnicodeFriendlyLinkExtractor(allow='(/marketreport/)((?!:).)*html$'),
             callback="parse_item", follow=True)
    ]

    def parse_item(self, response):
        cleaned_response = response.replace(
            body=response.body_as_unicode().encode('utf-8', 'ignore'),
            encoding='utf-8'
            )
        item = NewsArticleItem()
        try:
            title = response.xpath('//title/text()')[0].extract().encode('utf-8','ignore')
            raw_date = response.xpath('//font/text()')[2].extract().split(',')[1] + \
            response.xpath('//font/text()')[3].extract().split(',')[0]
            self.logger.info("Scraping Title: " + title)
            item['title'] = title.replace('Agrimoney.com | ', '').encode('utf-8','ignore')
            item['article'] = [art.encode('utf-8') for art in response.xpath('//body//text()').extract()]
            item['link'] = response.url.replace('http://', '').replace('https://', '').encode('utf-8','ignore')
        except UnicodeDecodeError:
            pass
        try:
            date = datetime.strptime(raw_date.split(',')[1].replace('Sept', 'Sep'), ' %d %b %Y')
            item['date'] = str(date)
            return item
        except (ValueError, IndexError):
            raw_date = response.xpath('//font/text()')[2].extract() + \
                response.xpath('//font/text()')[3].extract()
            try:
                date = datetime.strptime(raw_date.split(',')[2], ' %d %b %Y')
                item['date'] = str(date)
                return item
            except (ValueError, IndexError):
                try:
                    date = datetime.strptime(
                        raw_date.split(',')[1], ' %d %b %Y')
                    item['date'] = str(date)
                    return item
                except Exception as e:
                    pass
                    # self.logf.write("Failed to scrape {0}: {1}\n".format(
                    #    str(response.url), str(e)))
