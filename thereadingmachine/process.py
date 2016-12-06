import json
from itertools import islice
from nltk import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from nltk.stem.snowball import SnowballStemmer


def read_jsonl(input_file_name, **kwargs):
    print "Reading data from '{0}' ...".format(input_file_name)
    articles = []
    with open(input_file_name) as f:
        if 'size' in kwargs:
            subset = islice(f, kwargs['size'])
            for line in subset:
                articles.append(json.loads(line))
        else:
            for line in f:
                articles.append(json.loads(line))
    return articles


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
