import thereadingmachine.modeller.commodity_tagging as ctr
import thereadingmachine.environment as env
import thereadingmachine.utils.io as io


# Read and process data
articles = io.read_table(env.processed_article_table)
articles['article'] = articles['article'].apply(lambda x: x.split())
articles_list = articles.to_dict(orient='record')


# Tag commodity
commodity_tagged_articles = ctr.commodity_tag_article(articles=articles_list,
                                                      article_field='article',
                                                      id_field='id')

# Save back to database
io.save_table(data=commodity_tagged_articles,
              table_name=env.commodity_tagged_table,
              table_field_type=env.commodity_tagged_field_type)
