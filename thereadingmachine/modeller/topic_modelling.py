import pandas as pd
import numpy as np
import scipy as sp
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import NMF
from scipy.cluster.hierarchy import fcluster


class TopicModel(object):

    '''
    Main interface to a Topic Model Object
    '''

    def __init__(self,
                 n_features=10000,
                 n_topics=100,
                 remove_nouns=False):
        '''
        Create a new Topic Model.

        Parameters
        ----------
        n_features : number of features to use in the nmf decomposition
        n_topics : default number of topics
        Returns
        -------
        self : initialized topic model object
        '''
        self.nmf_topics = None
        self.nmf_labels = None
        self.tf = None
        self.nmf = None
        self.topic_dist = None
        self.n_features = n_features
        self.n_topics = n_topics
        self.linkage_matrix = None
        self.remove_nouns = remove_nouns

    def featurize(self, corpus):
        '''

        '''

        self.corpus = corpus
        self.tf_vectorizer = TfidfVectorizer(max_df=0.95,
                                             min_df=2,
                                             stop_words='english',
                                             analyzer='word',
                                             ngram_range=(1, 1),
                                             max_features=self.n_features)
        self.tf = self.tf_vectorizer.fit_transform(self.corpus)
        self.tf_feature_names = self.tf_vectorizer.get_feature_names()
        self.tf_freqs = [(word, self.tf.getcol(idx).sum())
                         for word, idx
                         in self.tf_vectorizer.vocabulary_.items()]
        self.tf_freqs = pd.DataFrame(self.tf_freqs, columns=('word', 'freq'))

    def fit(self, alpha=0, l1=0, n_topics=None):

        if n_topics is None:
            n_topics = [self.n_topics]
        self.nmf = dict()
        for k in n_topics:
            self.nmf[k] = NMF(n_components=k, random_state=1,
                              alpha=alpha, l1_ratio=l1).fit(self.tf)

    def get_topics(self, k=None):
        if k is None:
            k = self.n_topics

        self.nmf_topics = list()
        self.nmf_labels = list()

        self.nmf_documents_topics = pd.DataFrame(
            (self.nmf[k].components_ * self.tf.transpose()).transpose(),
            index=self.corpus.index)

        for topic_idx, topic in enumerate(self.nmf[k].components_):
            self.nmf_topics.append('Topic #%d: ' % topic_idx + ' '.join(
                [self.tf_feature_names[i] for i in topic.argsort()[:-11:-1]]))
            self.nmf_labels.append(
                '_'.join([self.tf_feature_names[x]
                          for x in topic.argsort()[-3:]]))

        self.nmf_labels = np.asarray(self.nmf_labels)
        self.nmf_documents_topics.columns = self.nmf_labels
        self.topic_dist = np.matrix(
            1 - cosine_similarity(self.nmf[k].components_))

    def cluster_topics(self, k=None, plot=False, save_fig=False):

        if k is None:
            k = self.n_topics

        if self.nmf_labels is None:
            self.get_topics(k)

        # define the linkage_matrix using ward clustering pre-computed
        # distances
        self.linkage_matrix = sp.cluster.hierarchy.ward(self.topic_dist)

    def prune_dendrogram(self, t=1):

        if self.linkage_matrix is None:
            self.cluster_topics()

        self.cluster_assignments = sp.cluster.hierarchy.fcluster(
            self.linkage_matrix, t=t)
        print '{0} clusters'.format(self.cluster_assignments.max())

        # maybe use the mean here?
        self.clustered_topics = self.nmf_documents_topics.apply(
            lambda x: x.groupby(self.cluster_assignments).mean(), axis=1)


def model_article_topic(articles, article_col='article', id_col='id'):
    '''Wrapper function to create a Topic Model instance, default
    n_features = 10000, n_topics = 100.
    '''

    model = TopicModel()

    # Featurize the corpus and fit the model
    model.featurize(articles[article_col])
    model.fit()

    # Extract the topics, defaulst to 100 topics
    model.get_topics()

    # Cluster of the topics
    model.cluster_topics(plot=True, save_fig=False)

    # Prune the dendogram
    cluster_assignments = fcluster(model.linkage_matrix, t=1.12)

    # Group loadings by cluster
    model.clustered_topics = (
        model.nmf_documents_topics.apply(
            lambda x: x.groupby(cluster_assignments).mean(),
            axis=1)
    )

    # Re-assign the id
    model.nmf_documents_topics[id_col] = articles[id_col]

    return model
