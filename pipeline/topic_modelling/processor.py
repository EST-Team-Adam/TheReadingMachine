import thereadingmachine.modeller.topic_modelling as ctr
import thereadingmachine.environment as env
import thereadingmachine.utils.io as io

# Read the data
articles = io.read_table(env.processed_article_table)

# Model article topics
model = ctr.model_article_topic(articles)

# Save the data back to the database
io.save_table(data=model.nmf_documents_topics,
              table_name=env.topic_model_table)
