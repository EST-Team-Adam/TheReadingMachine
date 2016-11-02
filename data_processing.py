import json
import nltk
from nltk import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn
from nltk.tokenize import RegexpTokenizer
from nltk.stem.snowball import SnowballStemmer


# Define functions
# --------------------------------------------------

# NOTE (Michael): The functions should reside in a package.


def process_text(text, lemmatization=True):
    '''The function process the texts with the intention for topic
    modelling.

    The following steps are performed:
    1. Tokenise
    2. Prune words
    3. Removal of stopwords

    Details:

    The regular expression tokeniser is used as we are interested just
    on the key words, punctuation is irrelevant.

    There are two options for word pruning, either stemming or
    lemmatisation.

    The standard snowball stemmer is currently implemented, however,
    for topic modelling we should consider lemmatisation over
    stemming.

    '''
    # Tokenize
    tokenizer = RegexpTokenizer(r'\w+')
    tokenized_text = tokenizer.tokenize(text)

    # Prune
    if lemmatization:
        lemmatizer = WordNetLemmatizer()
        pruned_text = [lemmatizer.lemmatize(word)
                       for word in tokenized_text]
    else:
        stemmer = SnowballStemmer("english")
        pruned_text = [stemmer.stem(word) for word in tokenized_text]

    # Remove stopwords
    nonstopword_text = [word.lower()
                        for word in pruned_text
                        if word not in set(stopwords.words('english'))]
    return nonstopword_text

# The topic and key word functions assumes that we know the topics
# already. For example, wheat, rice and soybean related topic.


def get_topic_keywords(topic):
    '''This function takes a a topic as a single character and returns
    keywords in the WordNet that are relevant.

    Relevancy is defined in the sense of hypernym, hyponym, meronym
    and holonyms.

    It is important to note that WordNet

    '''

    synsets = wn.synsets(topic)
    # NOTE (Michael): Need to think the level of synsets we need to
    #                 iterate.

    # Get hypernym synsets.
    hypernym_synsets = []
    [hypernym_synsets.extend(synset.hypernyms()) for synset in synsets]

    # Get hyponym synsets.
    hyponym_synsets = []
    [hyponym_synsets.extend(synset.hyponyms()) for synset in synsets]

    # Get part meronym synsets, part meronym are compmonents of the
    # object.
    part_meronyms_synsets = []
    [hyponym_synsets.extend(synset.part_meronyms())
     for synset in synsets]

    # Get substance meronym synsets, substance meronym are materials
    # of the object.
    substance_meronyms_synsets = []
    [hyponym_synsets.extend(synset.substance_meronyms())
     for synset in synsets]

    # Add the set together
    complete_synsets = hypernym_synsets + hyponym_synsets + \
        part_meronyms_synsets + substance_meronyms_synsets

    # Extract keywords of the synsets.
    keywords = []
    [keywords.extend(hyponym_synset.lemma_names())
     for hyponym_synset in complete_synsets]
    # NOTE (Michael): Porbably need to repalace '_' with space annd
    #                 try to match with collocation.
    return keywords


def extract_text_keywords(text, topic):
    '''This function takes a text and identifies keywords in the text
    that are related to a given topic.

    '''

    keywords = get_topic_keywords(topic)
    located_keywords = set([word
                            for word in text
                            if word in keywords])
    return located_keywords


# Reading data
# --------------------------------------------------

# Initiate file names and parameters
file_prefix = "data/amis_articles"
version = '27_07_2016'
input_file_name = '{0}_{1}.jsonl'.format(file_prefix, version)
test_sample_size = 1000

# Read the data
print "Reading data from '{0}' ...".format(input_file_name)
articles = []
with open(input_file_name) as f:
    for line in f:
        articles.append(json.loads(line))

# Take a sample for testing
test_sample = articles[:test_sample_size]


# Processing
# --------------------------------------------------

# TODO (Michael): Check why lemmatization resulted in more words.
for article in test_sample:
    article['processed_article'] = process_text(article['article'])

# Keyword Extraction
# --------------------------------------------------

# Pre define the topics
topics = ['wheat', 'rice', 'maize', 'soybean',
          'produce', 'trade', 'government', 'finance']

# Extract keywords
for article in test_sample:
    for topic in topics:
        article["{0}_keyword".format(topic).decode('UTF-8')] = \
            extract_text_keywords(article['processed_article'], topic)

# Subset articles that are related to wheat
wheat_articles = [article
                  for article in test_sample
                  if len(article['wheat_keyword']) > 0]
