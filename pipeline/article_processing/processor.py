import thereadingmachine.processor.article_processing as ctr
import thereadingmachine.environment as env
import thereadingmachine.parameter as param
import thereadingmachine.utils.io as io

# Read the data
articles = io.read_table(env.raw_article_table)

# Post processing the data extraction
processed_articles = ctr.scraper_post_processing(
    articles, model_start_date=param.model_start_date)

# Process the texts
preprocessed_text, text_summary = (
    ctr.text_preprocessing(article_df=processed_articles,
                           article_col='article',
                           min_length=param.min_length,
                           remove_captalisation=param.remove_captalisation,
                           remove_noun=param.remove_noun,
                           remove_numerical=param.remove_numerical,
                           remove_punctuation=param.remove_punctuation,
                           stem=param.stem))

# Save the data
io.save_table(data=preprocessed_text,
              table_name=env.processed_article_table,
              table_field_type=env.processed_article_field_type)

io.save_table(data=text_summary,
              table_name=env.processed_article_summary_table,
              table_field_type=env.processed_article_summary_field_type)
