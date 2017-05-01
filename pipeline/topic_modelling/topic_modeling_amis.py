import os
import pandas as pd
from sqlalchemy import create_engine
from scipy.cluster.hierarchy import fcluster
from topic_modeling import TopicModel


# Reading data
# --------------------------------------------------

data_dir = os.environ['DATA_DIR']
target_table = 'RawArticle'
engine = create_engine('sqlite:///{0}/the_reading_machine.db'.format(data_dir))
sql_query = 'SELECT * FROM {}'.format(target_table)
articles = pd.read_sql(sql_query, engine, parse_dates=['date'])

# Create a Topic Model instance, default n_features = 10000, n_topics = 100
model = TopicModel()

# Featurize the corpus and fit the model
model.featurize(articles['article'])
model.fit()

# Extract the topics, defaulst to 100 topics
model.get_topics()

# Cluster of the topics
model.cluster_topics(plot=True, save_fig=False)

# Prune the dendogram
cluster_assignments = fcluster(model.linkage_matrix, t=1.12)

# Group loadings by cluster
model.clustered_topics = model.nmf_documents_topics.apply(lambda x:
                                                          x.groupby(
                                                              cluster_assignments).mean(),
                                                          axis=1)


# Re-assign the id and save back to database
model.nmf_documents_topics['id'] = articles['id']
model.nmf_documents_topics.to_sql(con=engine, name='TopicModel',
                                  if_exists='replace',
                                  index=False)
