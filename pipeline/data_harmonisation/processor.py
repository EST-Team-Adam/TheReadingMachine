import thereadingmachine.environment as env
import thereadingmachine.processor.data_harmonisation as ctr
import thereadingmachine.utils.io as io

# Harmonise data
harmonised_article = (
    ctr.harmonise_article(pos_sentiment_col='positive_sentiment',
                          neg_sentiment_col='negative_sentiment',
                          id_col='id'))

# Save back to database
io.save_table(data=harmonised_article, table_name=env.harmonised_table)
