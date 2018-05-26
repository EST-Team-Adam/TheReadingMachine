import thereadingmachine.modeller.sentiment_scoring as ctr
import thereadingmachine.environment as env
import thereadingmachine.utils.io as io

# Read the data
articles = io.read_table(env.processed_article_table)
articles_list = articles.to_dict(orient='records')

# Score the articles
scored_articles = ctr.article_sentiment_scoring(
    articles=articles_list, article_col='article', id_col='id',
    date_col='date', method=['VADER', 'GOOGLE_NLP'], to_df=True)

# Save output file
io.save_table(data=scored_articles,
              table_name=env.sentiment_scored_table,
              table_field_type=env.sentiment_scored_field_type)
