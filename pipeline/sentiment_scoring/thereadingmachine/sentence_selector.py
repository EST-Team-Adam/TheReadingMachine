import re
import nltk
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
# Sentence Boundary Definition and some preliminary cleaning
from thereadingmachine.SBD import SBD
from thereadingmachine.sentence_keywords import sentence_keywords
from thereadingmachine.sentiment_VADER import VADER2
# from thereadingmachine.sentiment_GoogleNLP import GoogleNLP2


# sentence selector core script
def keyword_alarm(article_sentences, checkwords):
    stemmer = SnowballStemmer("english")
    selection = list()
    sentiment_VADER = list()
    # sentiment_Google = list()
    selected_sentences = list()
    for sentence in article_sentences:
        keywords_extractor = sentence_keywords(
            sentence)              # extracts the keywords
        keywords = list()
        keywords2 = list()
        # takes single words from extracted keywords
        for keyword in keywords_extractor:
            keywords.append(re.findall(r"[\w']+|[.,!?;]", keyword))
        keywords = sum(keywords, [])
        keywords = [word for word in keywords if word not in stopwords.words(
            'english')]    # stopwords removal
        for word in keywords:
            keywords2.append(stemmer.stem(word))
        if any(word in keywords2 for word in checkwords):
            selection.append(sentence)
            sentiment_VADER.append(VADER2(sentence))
            # sentiment_Google.append(GoogleNLP2(sentence))
            # , sentiment_Google)
            selected_sentences = zip(selection, sentiment_VADER)
    return selected_sentences


def wordslist(words_list):
    words_list1 = list()
    # by adding words here, they'll remove Kao's keywords
    commwords = ['wheat', 'rice', 'soybeans', 'soybean', 'maize', 'corn',
                 'grain', 'two-grain', 'wild', 'bean', 'oil', 'mays', 'grass',
                 'pearl', 'wall', 'common', 'little', 'milligram', 'wood']
    for word in words_list:
        tokens = list()
        tokens = nltk.word_tokenize(word)
        if any(word in commwords for word in tokens):
            word = ''
            words_list1.append(word)
            words_list1 = filter(None, words_list1)
        else:
            word = word
            words_list1.append(word)
    stemmer = SnowballStemmer("english")
    checkwords = list()
    checkwords2 = list()
    for word in words_list1:  # takes single words from extracted keywords
        checkwords.append(re.findall(r"[\w']+|[.,!?;]", word))
    # set() for avoiding multiple identical words
    checkwords = set(sum(checkwords, []))
    checkwords = [word for word in checkwords if word not in stopwords.words(
        'english')]      # stopwords removal
    for word in checkwords:
        checkwords2.append(stemmer.stem(word))
    return checkwords2


def sentences_analyzer(tests, checkwords):
    # checkwords = wordslist(checkwords)
    analyzed_sentences = list()
    # list_of_words = list()
    for test in tests:
        article_sentences = SBD(test, checkwords)
        dict = {'sentences': [], 'date': [], 'id': []}
        if len(keyword_alarm(article_sentences, checkwords)) > 0:
            dict['date'] = test['date']
            # resulting dict is dict['commodity'][number(article)][sentence]
            dict['sentences'] = keyword_alarm(article_sentences, checkwords)
            analyzed_sentences.append(dict)
    return analyzed_sentences
