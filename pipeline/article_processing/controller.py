from __future__ import division
import os
import itertools
import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from datetime import datetime

# Load and set some manipulation parameters
model_start_date = datetime.strptime(
    os.environ['MODEL_START_DATE'], '%Y-%m-%d').date()

maintenance_title = ['Reduced service at Agrimoney.com',
                     'Apology to Agrimoney.com subscribers']

irrelevant_link = ['https://www.euractiv.com/topics/news/?type_filter=video',
                   'http://www.euractiv.com/topics/news/?type_filter=video',
                   'http://www.euractiv.com/topics/news/?type_filter=news',
                   'http://www.euractiv.com/topics/news/?type_filter=all',
                   'https://www.euractiv.com/topics/news/?type_filter=all',
                   'https://www.euractiv.com/topics/news/',
                   'https://www.euractiv.com/topics/news/?type_filter=news',
                   'http://www.euractiv.com/topics/news/',
                   'https://www.euractiv.com/news/',
                   'http://www.euractiv.com/news/']


# Initialise processing parameters
remove_captalisation = True
remove_noun = True
remove_numerical = True
stem = False


def scraper_post_processing(raw_articles):

    # Remove the original id and drop duplciates
    processed_articles = (raw_articles
                          .drop('id', 1)
                          .drop_duplicates(subset='article'))

    # Remvoe entries that are associated with maintenance or service.
    processed_articles = processed_articles[~processed_articles['title'].isin(
        maintenance_title)]

    # Remoe links that are not associated with news articles.
    processed_articles = processed_articles[~processed_articles['link'].isin(
        irrelevant_link)]

    # Subset the data only after the model_start_date
    processed_articles = processed_articles[processed_articles['date']
                                            > model_start_date]

    # Recreate the index
    processed_articles.sort_values(['date'], ascending=[1], inplace=True)
    processed_articles['id'] = range(1, processed_articles.shape[0] + 1)

    return processed_articles


def text_processor(text, remove_captalisation=True, remove_noun=True,
                   remove_numerical=True, stem=False):
    '''The function process the texts with the intention for topic
    modelling.

    The following steps are performed:
    1. Tokenise
    2. Prune words
    3. Removal of stopwords

    Details:

    The regular expression tokeniser is used as we are interested just
    on the key words, punctuation is irrelevant.  There are two
    options for word pruning, either stemming or lemmatisation.  The
    standard snowball stemmer is currently implemented, however, for
    topic modelling we should consider lemmatisation over stemming.

    '''
    # TODO (Michael): Split words by '_', and maybe remove punctuations first.

    # Tokenize
    tokenizer = RegexpTokenizer(r'\w+')
    tokenized_text = tokenizer.tokenize(text)

    # # Prune
    # if lemmatization:
    #     lemmatizer = WordNetLemmatizer()
    #     pruned_text = [lemmatizer.lemmatize(word)
    #                    for word in tokenized_text]
    # else:
    #     stemmer = SnowballStemmer("english")
    #     pruned_text = [stemmer.stem(word) for word in tokenized_text]

    # This option is available as certain capital word has intrinsic
    # meaning. e.g. Apple vs apple.
    if remove_captalisation:
        tokenized_text = [word.lower() for word in tokenized_text]

    if remove_numerical:
        tokenized_text = [word for word in tokenized_text
                          if not word.isdigit()]

    # Remove stopwords and manual exlusion set
    meaningless_words = ['euractiv', 'com',
                         'bloomberg', 'reuters', 'jpg', 'png']
    exclusion_words = stopwords.words('english') + meaningless_words

    nonstopword_text = [word.lower()
                        for word in tokenized_text
                        if word.lower() not in exclusion_words]
    return nonstopword_text


def article_summariser(article_list):

    article_count = len(article_list)
    vocab_size = len(set(itertools.chain.from_iterable(article_list)))
    article_length = [len(t) for t in article_list]
    article_vocab_size = [len(set(t)) for t in article_list]
    lexical_diversity = [vs / l if l != 0 else 0
                         for l, vs in zip(article_length, article_vocab_size)]

    average_lexical_diversity = sum(lexical_diversity) / len(lexical_diversity)
    average_article_length = sum(article_length) / len(article_length)
    summary = {'createTime': datetime.utcnow(),
               'article_count': article_count,
               'vocab_size': vocab_size,
               'average_lexical_diversity': average_lexical_diversity,
               'average_article_length': average_article_length}
    return pd.DataFrame(summary, index=[0])


def text_preprocessing(article_df, article_col, min_length):
    tokenised_text = [text_processor(a,
                                     remove_captalisation=remove_captalisation,
                                     remove_noun=remove_noun,
                                     remove_numerical=remove_numerical,
                                     stem=stem)
                      for a in article_df[article_col]]

    min_length_ind = [i for i, t in enumerate(tokenised_text)
                      if len(t) > min_length]
    min_length_tokens = [tokenised_text[i] for i in min_length_ind]
    exclude_min_length_df = article_df.iloc[min_length_ind, ].copy()

    summary = article_summariser(min_length_tokens)
    exclude_min_length_df[article_col] = [' '.join(tt)
                                          for tt in min_length_tokens]
    return exclude_min_length_df, summary
