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
    selection = []
    sentiment_VADER = [None]
    sentiment_Google = [None]
    selected_sentences = []
    for sentence in article_sentences:
        keywords_extractor = sentence_keywords(sentence)              # extracts the keywords
        keywords = []
        keywords2 = []
        keywords = [re.findall(r"[\w']+|[.,!?;]", keyword) for keyword in keywords_extractor]
        keywords = sum(keywords,[])
        keywords = [word for word in keywords if word not in stopwords.words('english')]    # stopwords removal
        keywords2 = [stemmer.stem(word) for word in keywords]
        if any(word in keywords2 for word in checkwords):        
           selection.append(sentence)
           sentiment_VADER.append(VADER2(sentence))
           sentiment_Google.append(GoogleNLP2(sentence))
           selected_sentences = zip(selection, sentiment_VADER, sentiment_Google)
    return selected_sentences
  
  
def wordslist(words_list):    
    words_list1 = []
    commwords = ['wheat', 'rice', 'soybeans','soybean', 'maize','corn', 'grain','two-grain','wild','bean','oil','mays','grass','pearl','wall','common','little','milligram','wood']    # by adding words here, they'll remove Kao's keywords   
    for word in words_list:
        tokens = []
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
    checkwords = [re.findall(r"[\w']+|[.,!?;]", word) for word in words_list1]
    checkwords = [word for word in checkwords if word not in stopwords.words('english')]      # stopwords removal
    checkwords2 = [stemmer.stem(word) for word in checkwords]
    return checkwords2


def sentences_analyzer(tests, checkwords):              # analyzes just selected sentences
  analyzed_sentences = list()
  list_of_words = list()
  article_sentences = [SBD(test,checkwords) for test in tests]
  dict = {'sentences':[], 'date':[], 'id':[]}
  if len(keyword_alarm(article_sentences,checkwords))>0:
     dict['date'] = test['date']
     dict['id'] = test['id']
     dict['sentences'] = keyword_alarm(article_sentences,checkwords)   # resulting dict is dict['commodity'][number(article)][sentence]         
     analyzed_sentences.append(dict)
  return analyzed_sentences  


def all_sentences_analyzer(tests, counter):           # analyzes all the sentences
  all_sentences = list()
  sentiment_VADER = list()
  sentiment_Google = list()              # Activate this for Google NLP
  for test in tests:
      counter = counter + 1
      print counter
      article_sentences = list()
      dict = {'sentences':[], 'date':[], 'id':[]}
      article_sentences = sent_tokenize(textcleaner(test['article']))
      dict['date'] = test['date']
      dict['id'] = test['id']
      for sentence in article_sentences:
          sentiment_VADER.append(VADER2(sentence))
          sentiment_Google.append(GoogleNLP2(sentence))              # Activate this for Google NLP
          dict['sentences'] = zip(article_sentences, sentiment_VADER, sentiment_Google) 
      all_sentences.append(dict)
      print dict
  return all_sentences
  

def sentences_analyzer_twitter(tests, checkwords):    # selects and extracts sentences from twitter data
  analyzed_sentences = list()
  list_of_words = list()
  article_sentences = [SBD_twitter(test,checkwords) for test in tests]
  dict = {'sentences':[], 'date':[], 'id':[]}
  if len(keyword_alarm(article_sentences,checkwords))>0:
     dict['date'] = test['date']
     dict['id'] = test['id']
     dict['sentences'] = keyword_alarm(article_sentences,checkwords)   # resulting dict is dict['commodity'][number(article)][sentence]         
     analyzed_sentences.append(dict)
  return analyzed_sentences
  

  
def whole_articles(tests):     # whole articles analysis
    counter = 0
    results = list()
    for test in tests:
        dict = {'article':[], 'date':[], 'id':[], 'Google_NLP_detail':[], 'VADER':[],'Google_NLP':[]}
        counter = counter + 1
        dict['date'] = test['date']
        dict['article'] = test['article']
        dict['id'] = test['id']
        dict['Google_NLP_detail'] = GoogleNLP2(test['article'])
        dict['VADER'] = VADER2(test['article'])
        try:
            dict['Google_NLP'] = dict['Google_NLP_detail']['polarity'] * dict['Google_NLP_detail']['magnitude']
        except KeyboardInterrupt:
            raise
        except:
            print 'No Google NLP Sentiment'
        #print dict
        print counter
        results.append(dict)
        #print results
    return results
    
    

def articles_sentiment(all_sentences):                        # new version, directly linked to all_sentences
    articles_sentiment_scores = [None] * len(all_sentences)
    for article in all_sentences:
        dic = {'date':[], 'id':[], 'positive_sentiment':[], 'neutral_sentiment':[], 'negative_sentiment':[], 'compound_sentiment':[], 'google_sentiment':[]}
        VADER_article_sentiment = [0] * 4
        GOOGLE_article_sent = [0]
        VADER_sentiment_pos = list()
        VADER_sentiment_neu = list()
        VADER_sentiment_neg = list()
        VADER_sentiment_compound = list()
        GOOGLE_sentiment = [0]
        for sentence in article['sentences']:
            #print sentence
            VADER_sentiment_pos.append(sentence[1]['pos'])
            VADER_sentiment_neu.append(sentence[1]['neu'])
            VADER_sentiment_neg.append(sentence[1]['neg'])
            VADER_sentiment_compound.append(sentence[1]['compound'])
            try:
                GOOGLE_sentiment.append(sentence[2]['polarity'] * sentence[2]['magnitude'])
            except:
                pass
        VADER_article_sentiment[0] = np.mean(VADER_sentiment_pos)
        VADER_article_sentiment[1] = np.mean(VADER_sentiment_neu)
        VADER_article_sentiment[2] = np.mean(VADER_sentiment_neg)
        VADER_article_sentiment[3] = np.mean(VADER_sentiment_compound)
        GOOGLE_article_sent = np.mean(GOOGLE_sentiment)
        dic['date'] = article['date']
        dic['id'] = article['id']
        dic['positive_sentiment'] = VADER_article_sentiment[0]
        dic['neutral_sentiment'] = VADER_article_sentiment[1]
        dic['negative_sentiment'] = VADER_article_sentiment[2]
        dic['compound_sentiment'] = VADER_article_sentiment[3]
        dic['google_sentiment'] = GOOGLE_article_sent
        articles_sentiment_scores.append(dic)
    return articles_sentiment_scores