import json
from itertools import islice
from operator import itemgetter
from datetime import datetime
from nltk import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from nltk.stem.snowball import SnowballStemmer
from keyword import tag_commodity


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


def extract_date(input_file_name, output_file_name):
    with open(input_file_name) as fi, open(output_file_name, 'w') as fo:
        for line in fi:
            article = json.loads(line)
            json.dump({'id': article['id'], 'date': article['date']}, fo)
            fo.write('\n')


def extract_geo(input_file_name, output_file_name):
    with open(input_file_name) as fi, open(output_file_name, 'w') as fo:
        for line in fi:
            geo_tagged = json.loads(line)
            geo_dict = {'id': geo_tagged['id'],
                        'geo_tag': geo_tagged['geo_tag']}
            json.dump(geo_dict, fo)
            fo.write('\n')


def extract_commodity(input_file_name, output_file_name, wheat_keywords,
                      rice_keywords, maize_keywords, barley_keywords,
                      soybean_keywords, grains_keywords):
    with open(input_file_name) as fi, open(output_file_name, 'w') as fo:
        for line in fi:
            article = json.loads(line)
            tagged_article = tag_commodity(article,
                                           wheat_keywords=wheat_keywords,
                                           rice_keywords=rice_keywords,
                                           maize_keywords=maize_keywords,
                                           soybean_keywords=soybean_keywords,
                                           grain_keywords=grains_keywords)
            tagged_article.update({'id': article['id']})
            json.dump(tagged_article, fo)
            fo.write('\n')


def index_article(articles):
    # Convert date string to date class
    for article in articles:
        article.update({'date': datetime.strptime(article.get('date'),
                                                  '%Y-%m-%d %H:%M:%S')})

        # Sort the article
        articles = sorted(articles, key=itemgetter('date'))

        # Create pk
        [article.update({'id': ('a' + str(index).zfill(8))})
         for index, article in enumerate(articles)]

        # Convert date back to string
        for article in articles:
            article.update({'date': str(article.get('date'))})

    return article
