import thereadingmachine.scraper.article_scraper as ctr
import thereadingmachine.environment as env

# 'bloomberg' removed temporarily.
ctr.scrap_articles(env.spiders)
