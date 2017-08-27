from __future__ import division
import itertools
import pandas as pd
import string
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from nltk.stem import SnowballStemmer
from nltk import pos_tag
from datetime import datetime


# Manual invalid title and link
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


def scraper_post_processing(raw_articles, model_start_date):
    '''Perform post processing of articles scrapped by the scrapper.

    There have been a few issues identified regarding the
    scraper. Certain issues are either impossible or difficult to
    eliminate with the scrapy implementation. Thus, we post process
    the data to resolve these known issues.

    '''

    # If an ID has already been created, then we drop it.
    if 'id' in raw_articles.columns:
        raw_articles = raw_articles.drop('id', 1)

    # Drop duplciates based on article content
    processed_articles = (raw_articles
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

    return processed_articles


def text_processor(text, remove_captalisation=True, remove_noun=False,
                   remove_numerical=True, remove_punctuation=True,
                   stem=False, tokenizer=None):
    '''The function process the texts with the intention for topic
    modelling.

    The following steps are performed:
    1. Tokenise
    2. Prune words
    3. Removal of stopwords

    Details:

    The regular expression tokeniser is used as we are interested just
    on the key words, punctuation is irrelevant. Numerical and
    captalisation removal can be specified as a parameter. Stop words
    and certain manually coded phrases are also removed.

    NOTE(Michael): The remove_noun is currently inactive. Further
                    investigation is required for the implementation.

    '''

    # Tokenize
    if tokenizer is None:
        tokenizer = RegexpTokenizer(r'\w+')
        tokenized_text = tokenizer.tokenize(text)
    else:
        tokenized_text = tokenizer(text)

    if remove_punctuation:
        punct = string.punctuation
        tokenized_text = [t for t in tokenized_text if t not in punct]

    # This step is extremely computational expensive. The benchmark
    # shows it would increase the total time by 12 times.
    if remove_noun:
        noun_set = set(['NNP', 'NNPS'])
        tokenized_text = [w for w, t in pos_tag(tokenized_text)
                          if t not in noun_set]
    # Stemming
    if stem:
        stemmer = SnowballStemmer('english')
        tokenized_text = [stemmer.stem(word) for word in tokenized_text]

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

    nonstopword_text = [word
                        for word in tokenized_text
                        if word.lower() not in exclusion_words]
    return nonstopword_text


def article_summariser(article_list):
    '''Function to summarise the processing of the article text.

    The purpose of this summary is to identify any significant changes
    to the text extraction and processing.

    '''

    article_count = len(article_list)
    vocab_size = len(set(itertools.chain.from_iterable(article_list)))
    article_length = [len(t) for t in article_list]
    article_vocab_size = [len(set(t)) for t in article_list]
    lexical_diversity = [vs / l if l != 0 else 0
                         for l, vs in zip(article_length, article_vocab_size)]

    average_lexical_diversity = sum(lexical_diversity) / len(lexical_diversity)
    average_article_length = sum(article_length) / len(article_length)

    # TODO (Michael): Should also save the data sources.
    summary = {'createTime': datetime.utcnow(),
               'article_count': article_count,
               'vocab_size': vocab_size,
               'average_lexical_diversity': average_lexical_diversity,
               'average_article_length': average_article_length}

    return pd.DataFrame(summary, index=[0])


def text_preprocessing(article_df, article_col, min_length,
                       remove_captalisation=True, remove_noun=False,
                       remove_numerical=True, remove_punctuation=True,
                       stem=False):
    '''Process the text extracted from the scrapper.

    In addition, articles with tokens less than the min_length
    specified will be dropped. This is because certain articles were
    extracted incorrectly or contains insufficient information, thus
    they are removed to avoid contamination of the output.

    '''

    # Tokenise and process the text
    tokenised_text = [text_processor(a,
                                     remove_captalisation=remove_captalisation,
                                     remove_noun=remove_noun,
                                     remove_numerical=remove_numerical,
                                     remove_punctuation=remove_punctuation,
                                     stem=stem)
                      for a in article_df[article_col]]

    # Find the index of entries where the article length is less than
    # the specified length. The entries are then removed from the
    # article and the original data frame.
    min_length_ind = [i for i, t in enumerate(tokenised_text)
                      if len(t) > min_length]
    min_length_tokens = [tokenised_text[i] for i in min_length_ind]
    exclude_min_length_df = article_df.iloc[min_length_ind, ].copy()

    # Create the summary
    summary = article_summariser(min_length_tokens)

    # Concatenate the text together. This step is to enable the result
    # to be saved in to a standard database.
    exclude_min_length_df[article_col] = [' '.join(tt)
                                          for tt in min_length_tokens]

    # Recreate the index
    exclude_min_length_df.sort_values(['date'], ascending=[1], inplace=True)
    exclude_min_length_df['id'] = range(1, exclude_min_length_df.shape[0] + 1)

    return exclude_min_length_df, summary
