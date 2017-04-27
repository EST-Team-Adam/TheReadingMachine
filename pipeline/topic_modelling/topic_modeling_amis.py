import pandas as pd
import json

from topic_modeling import TopicModel


# Reading data
# --------------------------------------------------

# Initiate file names and parameters
file_prefix = "data/amis_articles"
version = '27_11_2016'
input_file_name = '{0}_{1}_indexed.jsonl'.format(file_prefix, version)
output_file_name = "topic_model.pkl"

# Load articles
with open(input_file_name) as f:
    articles = pd.DataFrame(json.loads(line) for line in f)
articles['date'] = pd.to_datetime(articles['date'])
articles = articles.set_index(articles.id)

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
cluster_assignments = sp.cluster.hierarchy.fcluster(model.linkage_matrix, t=1.12)

# Group loadings by cluster
model.clustered_topics = model.nmf_documents_topics.apply(lambda x: 
    x.groupby(cluster_assignments).mean(), axis=1)


# Save the topics in pkl file
model.nmf_documents_topics.to_picke(output_file_name)


