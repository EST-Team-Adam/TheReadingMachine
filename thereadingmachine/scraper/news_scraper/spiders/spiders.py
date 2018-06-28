import pandas as pd
from datetime import datetime
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import HtmlXPathSelector
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.utils.response import get_base_url
from scrapy.exceptions import DropItem
from scrapy.utils.project import get_project_settings
from scrapy.http import HtmlResponse
import thereadingmachine.environment as env
from thereadingmachine.scraper.news_scraper.items import NewsArticleItem


class UnicodeFriendlyLinkExtractor(LxmlLinkExtractor):
    '''Need this to fix the encoding error.

    Taken from
    https://stackoverflow.com/questions/17862016/scrapy-python-unicode-links-error

    '''

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

        links = self._extract_links(
            body, response.url, response.encoding, base_url)
        links = self._process_links(links)
        return links


class AmisCrawlSpider(CrawlSpider):

    def __init__(self, *a, **kw):
        '''Initialize the full set of seen links
        '''

        self.only_new = get_project_settings().get('SCRAPE_ONLY_NEW')
        if self.only_new:
            # NOTE (Michael): This is to account for first time check when
            #                 the table does not exist.
            try:
                link_query = 'SELECT DISTINCT link FROM RawArticle'
                self.seen_links = set(pd.read_sql(
                    link_query, env.engine).link.unique())
                print('{} links scraped in previous rounds'.format(
                    len(self.seen_links)))
            except:
                self.seen_links = set()
        else:
            self.seen_links = set()

        super(AmisCrawlSpider, self).__init__(*a, **kw)

    def _requests_to_follow(self, response):
        if not isinstance(response, HtmlResponse):
            return
        seen = self.seen_links
        for n, rule in enumerate(self._rules):
            links = [lnk
                     for lnk in rule.link_extractor.extract_links(response)
                     if lnk not in seen]
            if links and rule.process_links:
                links = rule.process_links(links)
            for link in links:
                seen.add(link)
                r = self._build_request(n, link)
                yield rule.process_request(r)


class BloombergSpider(AmisCrawlSpider):
    name = 'bloomberg'
    allowed_domains = ['bloomberg.com']
    start_urls = ['http://www.bloomberg.com']
    rules = [
        Rule(UnicodeFriendlyLinkExtractor(allow='(/news/articles/)((?!:).)*$'),
             callback='parse_item', follow=True),
        Rule(UnicodeFriendlyLinkExtractor(allow='(/news/)((?!:).)*$'),
             callback='parse_item', follow=True),
        Rule(UnicodeFriendlyLinkExtractor(allow='(/articles/)((?!:).)*$'),
             callback='parse_item', follow=True)
    ]

    def parse_item(self, response):
        item = NewsArticleItem()
        title = response.xpath('//title/text()').extract_first()
        if title == 'Bloomberg':
            title = response.xpath(
                '//meta[@property="og:title"]/text()').extract_first()

        article = response.xpath('//p/text()').extract()
        self.logger.info('Scraping Title: ' + title)
        try:
            item['title'] = title
            item['article'] = article
            item['link'] = response.url
            raw_date = response.url.split('/')[-2]
            date = datetime.strptime(raw_date, '%Y-%m-%d')
            item['date'] = str(date)
            return item
        except Exception as e:
            pass


class NoggersBlogSpider(AmisCrawlSpider):
    name = 'noggers'
    allowed_domains = ["nogger-noggersblog.blogspot.com",
                       "nogger-noggersblog.blogspot.co.id",
                       "nogger-noggersblog.blogspot.ch"]
    start_urls = ["http://nogger-noggersblog.blogspot.com/"]
    rules = [
        Rule(UnicodeFriendlyLinkExtractor(allow='((?!:).)*html$'),
             callback='parse_item', follow=True)
    ]

    def parse_item(self, response):
        item = NewsArticleItem()
        title = response.xpath('//a/text()')[8].extract()
        article = response.xpath('//div/text()').extract()
        self.logger.info('Scraping Title: ' + title)
        item['title'] = title
        item['article'] = article
        item['link'] = response.url

        try:
            token = filter(lambda x: '--' in x, article)
            try:
                raw_date = token[0].split(' -- ')[0].replace('\n', '')
                date = datetime.strptime(raw_date, '%d/%m/%y')
            except (ValueError, IndexError):
                try:
                    raw_date = title.split("Nogger's Blog: ")[1]
                    date = datetime.strptime(raw_date, '%d-%b-%Y')
                except (ValueError, IndexError):
                    date = ''
            item['date'] = str(date)
            return item
        except Exception as e:
            pass


class WorldGrainSpider(AmisCrawlSpider):

    def _parse_wg_date(self, ds):
        for fmt in ('%B %d, %Y', '%b. %d, %Y', '%m/%d/%Y'):
            try:
                return(datetime.strptime(ds, fmt))
            except ValueError:
                pass
        raise ValueError('no valid date format found for ' + ds)

    def _clean_date(self, raw):
        clean = (raw.replace('\t', '')
                 .replace('\n', '')
                 .replace('-', '')
                 .replace('WorldGrain.com,', '')
                 .replace('Decemebr', 'December')
                 .replace('janaury', 'January')
                 .replace('Aprll', 'April')
                 .replace('Sept.', 'September')
                 .strip())

        return(clean)

    name = 'worldgrain'
    allowed_domains = ['world-grain.com']
    start_urls = ['http://www.world-grain.com'] + \
        ['http://www.world-grain.com/News/Archive.aspx?page={0}&year={1}&month=0'.format(i, j)
         for i in range(1, 100) for j in range(2006, 2017)]
    rules = [
        Rule(UnicodeFriendlyLinkExtractor(allow='(/articles/news_home/)((?!:).)*$',
                                          deny='(m.world-grain.com)((?!:).)*$'),
             callback='parse_item', follow=True),
        Rule(UnicodeFriendlyLinkExtractor(allow='(/news_home/)((?!:).)*$',
                                          deny='(m.world-grain.com)((?!:).)*$'),
             callback='parse_item', follow=True),
        Rule(UnicodeFriendlyLinkExtractor(allow='(/articles/)((?!:).)*$',
                                          deny='(m.world-grain.com)((?!:).)*$'),
             callback='parse_item', follow=True)
    ]

    def parse_item(self, response):
        item = NewsArticleItem()
        title = response.xpath('//title/text()').extract_first()
        article = (
            response.xpath('//p/text()').extract() +
            response.xpath('//br/text()').extract() +
            response.xpath('//div[@class="article"]/text()').extract() +
            response.xpath(
                '//div["font-family: arial; font-size: 13px"]/text()')
            .extract())

        self.logger.info('Scraping Title: ' + title)
        item['title'] = title
        item['article'] = article
        item['link'] = response.url

        raw_date = (response.xpath('//span[@class="news_article_date"]/text()')
                    .extract_first()
                    or response.xpath('//td[@class="pubName"]/text()')
                    .extract_first())
        clean_date = self._parse_wg_date(self._clean_date(raw_date))
        if clean_date.year < 1900:
            raise DropItem('Incorrect Format for Date in %s' % item)
        else:
            item['date'] = str(clean_date)
        return item


class EuractivSpider(AmisCrawlSpider):
    name = 'euractiv'
    allowed_domains = ['www.euractiv.com']
    start_urls = ['http://www.euractiv.com']
    rules = [
        Rule(UnicodeFriendlyLinkExtractor(allow='(/agriculture-food/news/)((?!:).)*$'),
             callback='parse_item', follow=True),
        Rule(UnicodeFriendlyLinkExtractor(allow='(/news/)((?!:).)*$'),
             callback='parse_item', follow=True)
    ]

    def parse_item(self, response):
        item = NewsArticleItem()
        try:
            title = response.xpath('//title/text()')[0].extract()
            article = response.xpath('//p/text()').extract()
            item['title'] = title
            item['article'] = article
            item['link'] = response.url
        except UnicodeDecodeError:
            pass

        self.logger.info('Scraping Title: ' + title)

        try:
            raw_date = response.xpath(
                '//*[contains(@class,"ea-dateformat")]/text()').extract()[1].strip()
            date = datetime.strptime(raw_date, '%d-%m-%Y')
            item['date'] = str(date)
            return item
        except Exception as e:
            pass


class AgriMoneySpider(AmisCrawlSpider):
    name = 'agrimoney'
    # logf = open('logs/agrimoney.log', 'w')
    allowed_domains = ['www.agrimoney.com']
    start_urls = [
        'http://www.agrimoney.com',
        'http://www.agrimoney.com/search/',
        'http://www.agrimoney.com/searchdate/'
    ] + ['http://www.agrimoney.com/search/{0}/'.format(i) for i in range(600)] + \
        ['http://www.agrimoney.com/searchdate/{0}/'.format(i)
         for i in range(500)]
    deny_links = ('(/reduced-service-at-agrimoney.com)((?!:).)*html$',
                  '(/apology-to-agrimoney.com-subscribers)((?!:).)*html$')
    rules = [
        Rule(UnicodeFriendlyLinkExtractor(allow='(/news/)((?!:).)*html$',
                                          deny=deny_links),
             callback='parse_item', follow=True),
        Rule(UnicodeFriendlyLinkExtractor(allow='(/feature/)((?!:).)*html$',
                                          deny=deny_links),
             callback='parse_item', follow=True),
        Rule(UnicodeFriendlyLinkExtractor(allow='(/marketreport/)((?!:).)*html$',
                                          deny=deny_links),
             callback='parse_item', follow=True)
    ]

    def parse_item(self, response):
        # NOTE (Michael): This is not used, review required.
        #
        # cleaned_response = response.replace(
        #     body=response.body_as_unicode().encode('utf-8', 'ignore'),
        #     encoding='utf-8'
        # )
        item = NewsArticleItem()
        try:
            title = response.xpath(
                '//title/text()')[0].extract().encode('utf-8', 'ignore')
            raw_date = response.xpath('//font/text()')[2].extract().split(',')[1] + \
                response.xpath('//font/text()')[3].extract().split(',')[0]
            self.logger.info('Scraping Title: ' + title)
            item['title'] = title.replace(
                'Agrimoney.com | ', '').encode('utf-8', 'ignore')
            item['article'] = [art.encode(
                'utf-8') for art in response.xpath('//body//text()').extract()]
            item['link'] = response.url
        except UnicodeDecodeError:
            pass
        try:
            date = datetime.strptime(raw_date.split(
                ',')[1].replace('Sept', 'Sep'), ' %d %b %Y')
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
