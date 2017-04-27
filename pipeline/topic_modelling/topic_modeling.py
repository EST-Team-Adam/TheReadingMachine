import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from scipy.cluster.hierarchy import ward, dendrogram
from sklearn.decomposition import NMF
import nltk
from sklearn.feature_extraction import text
import matplotlib.pyplot as plt


from utils import preprocessor


class TopicModel(object):

    """
    Main interface to a Topic Model Object
    """

    def __init__(self,
                 n_features = 10000,
                 n_topics=100):  
        """
        Create a new Topic Model.

        Parameters
        ----------
        n_features : number of features to use in the nmf decomposition
        n_topics : default number of topics
        Returns
        -------
        self : initialized topic model object
        """
        self.nmf_topics = None
        self.nmf_labels = None
        self.tf = None
        self.nmf = None
        self.topic_dist = None
        self.n_features = n_features
        self.n_topics = n_topics
        self.linkage_matrix = None
    

    def featurize(self, corpus):
        """

        """
    	self.corpus = corpus.apply(lambda x: preprocessor(x.decode('utf-8')))
    	self.tf_vectorizer = text.CountVectorizer(
    		max_df=.95, 
    		min_df=2, 
    		ngram_range=(1, 1),
    		max_features=self.n_features, 
    		tokenizer=nltk.word_tokenize,
    		stop_words=list(text.ENGLISH_STOP_WORDS))
    	self.tf = self.tf_vectorizer.fit_transform(self.corpus)
    	self.tf_feature_names = self.tf_vectorizer.get_feature_names()
    	self.tf_freqs = [(word, self.tf.getcol(idx).sum()) for word, idx in self.tf_vectorizer.vocabulary_.items()]
    	self.tf_freqs = pd.DataFrame(self.tf_freqs, columns=('word', 'freq'))


    def fit(self, alpha=0, l1=0, n_topics=None):
    	
    	if n_topics is None:
    		n_topics = [self.n_topics]
    	self.nmf = dict()

        #self.reconstruction_error = pd.DataFrame(index=np.arange(0, len(n_topics)), 
        #    columns = ('n_components', 'alpha', 'l1_ratio', 'reconstruction_error'))
        
        #n = 0
    	for k in n_topics:
    		self.nmf[k] = NMF(n_components=k, random_state=1, alpha=alpha, l1_ratio=l1).fit(self.tf)
    		#self.reconstruction_error.loc[n] = [k, alpha, l1, self.nmf[k].reconstruction_err_]
            #n = n + 1
        #print self.reconstruction_error

    def get_topics(self, k=None):
    	if k is None:
    		k = self.n_topics

    	self.nmf_topics = list()
    	self.nmf_labels=list()

    	self.nmf_documents_topics = pd.DataFrame((self.nmf[k].components_ * self.tf.transpose()).transpose(),
         index=self.corpus.index)

    	for topic_idx, topic in enumerate(self.nmf[k].components_):
    		#print("Topic #%d: " % topic_idx + " ".join([self.tf_feature_names[i] for i in topic.argsort()[:-51:-1]]))
    		self.nmf_topics.append("Topic #%d: " % topic_idx + " ".join([self.tf_feature_names[i] for i in topic.argsort()[:-11:-1]]))
    		self.nmf_labels.append(" ".join([self.tf_feature_names[x] for x in topic.argsort()[-3:]]))

    	self.nmf_labels = np.asarray(self.nmf_labels)
        self.nmf_documents_topics.columns = self.nmf_labels
        self.topic_dist = np.matrix(1 - cosine_similarity(self.nmf[k].components_))

        topic_min_dist = np.where(self.topic_dist == self.topic_dist[np.where(self.topic_dist > 0.01)].min())[0]

        #print('The two closest Topics have a cosine similarity of ' + str(self.topic_dist[np.where(self.topic_dist >.6)].min()))
        #print('')
        #print('Topic 1: ' + str(self.nmf_topics[topic_min_dist[0]]))
        #print('')
        #print('Topic 2: ' + str(self.nmf_topics[topic_min_dist[1]]))


    def cluster_topics(self, k=None, plot=False, save_fig=False):
        
        if k is None:
            k = self.n_topics
        
        if self.nmf_labels is None:
            self.get_topics(k)

        self.linkage_matrix = ward(self.topic_dist) # define the linkage_matrix using ward clustering pre-computed distances
        
        if plot:
            fig, ax = plt.subplots(figsize=(10, 60)) # set size
            ax = dendrogram(self.linkage_matrix, orientation="left", labels=np.array(self.nmf_labels), leaf_font_size=16)
            #plt.tick_params(axis= 'x', which='both', bottom='off', top='off', labelbottom='off')
            plt.tight_layout()
            if save_fig:
                plt.savefig('topic_heirarchy.png', dpi=200) #save figure as ward_clusters

    def prune_dendrogram(self, t=1):

        if self.linkage_matrix is None:
            self.cluster_topics()

        self.cluster_assignments = sp.cluster.hierarchy.fcluster(self.linkage_matrix, t=t)
        print "{0} clusters".format(self.cluster_assignments.max())

        # maybe use the mean here?
        self.clustered_topics = self.nmf_documents_topics.apply(lambda x: x.groupby(self.cluster_assignments).mean(), axis=1)

