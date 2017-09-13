import controller as ctr

# 'bloomberg' removed temporarily.
spiders = ['noggers', 'worldgrain', 'euractiv', 'agrimoney']
ctr.scrap_articles(spiders)

# Save output file
ctr.save_json_to_db(spiders)
