import thereadingmachine.modeller.geo_tagging as ctr
import thereadingmachine.environment as env
import thereadingmachine.utils.io as io


# Read the data
articles = io.read_table(env.processed_article_table)
articles_dict = articles.to_dict(orient='records')


# Read country list
country_list = ctr.read_countries(env.country_file)
country_dict = ctr.country_list_to_dict(country_list)

# Geotag articles
geotagged_articles = ctr.geotag_article(
    articles=articles_dict, country_dict=country_dict)


# Save output file
io.save_table(data=geotagged_articles,
              table_name=env.geo_tagged_table,
              table_field_type=env.geo_tagged_field_type)
