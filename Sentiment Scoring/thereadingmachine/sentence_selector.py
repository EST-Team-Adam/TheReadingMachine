import re
from nltk.corpus import stopwords
import nltk
from thereadingmachine.SBD import SBD  
from thereadingmachine.SBD import SBD_twitter                                      # Sentence Boundary Definition and some preliminary cleaning
from thereadingmachine.sentence_keywords import sentence_keywords
from nltk.stem.snowball import SnowballStemmer
from thereadingmachine.sentiment_VADER import VADER2
from thereadingmachine.sentiment_GoogleNLP import GoogleNLP2
from nltk.tokenize import sent_tokenize                    # for the all sentences analysis
from thereadingmachine.textcleaner import textcleaner      # for the all sentences analysis
import numpy as np    # for a unique sentiment score per each article


def keyword_alarm(article_sentences, checkwords):               # sentence selector core script
    stemmer = SnowballStemmer("english")
    selection = list()
    sentiment_VADER = list()
    #sentiment_Google = list()
    selected_sentences = list()
    for sentence in article_sentences:
        keywords_extractor = sentence_keywords(sentence)              # extracts the keywords
        keywords = list()
        keywords2 = list()
        for keyword in keywords_extractor:                            # takes single words from extracted keywords
            keywords.append(re.findall(r"[\w']+|[.,!?;]", keyword))
        keywords = sum(keywords,[])
        keywords = [word for word in keywords if word not in stopwords.words('english')]    # stopwords removal
        for word in keywords:
            keywords2.append(stemmer.stem(word))
        if any(word in keywords2 for word in checkwords):        
           selection.append(sentence)
           sentiment_VADER.append(VADER2(sentence))
           #sentiment_Google.append(GoogleNLP2(sentence))
           selected_sentences = zip(selection, sentiment_VADER)#, sentiment_Google)
    return selected_sentences
  
  
def wordslist(words_list):    
    words_list1 = list()
    commwords = ['wheat', 'rice', 'soybeans','soybean', 'maize','corn', 'grain','two-grain','wild','bean','oil','mays','grass','pearl','wall','common','little','milligram','wood']    # by adding words here, they'll remove Kao's keywords   
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
    for word in words_list1:                            # takes single words from extracted keywords
        checkwords.append(re.findall(r"[\w']+|[.,!?;]", word))
    checkwords = set(sum(checkwords,[]))               # set() for avoiding multiple identical words
    checkwords = [word for word in checkwords if word not in stopwords.words('english')]      # stopwords removal
    for word in checkwords:
        checkwords2.append(stemmer.stem(word))
    return checkwords2


def sentences_analyzer(tests, checkwords):              # analyzes just selected sentences
  #checkwords = wordslist(checkwords)  
  analyzed_sentences = list()
  list_of_words = list()
  for test in tests:
      article_sentences = SBD(test,checkwords)
      dict = {'sentences':[], 'date':[], 'id':[]}
      if len(keyword_alarm(article_sentences,checkwords))>0:
         dict['date'] = test['date']
         dict['id'] = test['id']
         dict['sentences'] = keyword_alarm(article_sentences,checkwords)   # resulting dict is dict['commodity'][number(article)][sentence]         
         analyzed_sentences.append(dict)
  return analyzed_sentences  


def all_sentences_analyzer(tests):           # analyzes all the sentences
  all_sentences = list()
  sentiment_VADER = list()
  #sentiment_Google = list()              # Activate this for Google NLP
  for test in tests:
      article_sentences = list()
      dict = {'sentences':[], 'date':[], 'id':[]}
      article_sentences = sent_tokenize(textcleaner(test['article']))
      dict['date'] = test['date']
      dict['id'] = test['id']
      for sentence in article_sentences:
          sentiment_VADER.append(VADER2(sentence))
          #sentiment_Google.append(GoogleNLP2(sentence))              # Activate this for Google NLP
      dict['sentences'] = zip(article_sentences, sentiment_VADER)#, sentiment_Google)  
      all_sentences.append(dict)
  return all_sentences
  

def sentences_analyzer_twitter(tests, checkwords):    # selects and extracts sentences from twitter data
  #checkwords = wordslist(checkwords)  
  analyzed_sentences = list()
  list_of_words = list()
  for test in tests:
      article_sentences = SBD_twitter(test,checkwords)
      dict = {'sentences':[], 'date':[], 'id':[]}
      if len(keyword_alarm(article_sentences,checkwords))>0:
         dict['date'] = test['date']
         dict['id'] = test['id']
         dict['sentences'] = keyword_alarm(article_sentences,checkwords)   # resulting dict is dict['commodity'][number(article)][sentence]         
         analyzed_sentences.append(dict)
  return analyzed_sentences


def articles_sentiment(analyzed_sentences):      # computes a unique sentiment score per each article using the mean
    articles_sentiment_scores = list()
    for item in analyzed_sentences:
        dic = {'date':[], 'id':[], 'positive_sentiment':[], 'neutral_sentiment':[], 'negative_sentiment':[], 'compound_sentiment':[]}
        positive_sentiment = list()
        neutral_sentiment = list()
        negative_sentiment = list()
        compound_sentiment = list()
        article_pos_sent = list()
        article_neu_sent = list()
        article_neg_sent = list()
        article_compound_sent = list()
        for sentence in item['sentences']:
            positive_sentiment.append(sentence[1]['pos'])
            neutral_sentiment.append(sentence[1]['neu'])
            negative_sentiment.append(sentence[1]['neg'])
            compound_sentiment.append(sentence[1]['compound'])    # these lists are just for the last one
        article_pos_sent = np.mean(positive_sentiment)
        article_neu_sent = np.mean(neutral_sentiment)
        article_neg_sent = np.mean(negative_sentiment)
        article_compound_sent = np.mean(compound_sentiment)
        dic['date'] = item['date']
        dic['id'] = item['id']
        dic['positive_sentiment'] = article_pos_sent
        dic['neutral_sentiment'] = article_neu_sent
        dic['negative_sentiment'] = article_neg_sent
        dic['compound_sentiment'] = article_compound_sent
        articles_sentiment_scores.append(dic)
    return articles_sentiment_scores
