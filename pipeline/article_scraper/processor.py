import thereadingmachine.scraper.article_scraper as ctr
import thereadingmachine.environment as env

# 'bloomberg' removed temporarily.
ctr.scrap_articles(env.spiders)

# Save output file
ctr.save_json_to_db(env.spiders)
