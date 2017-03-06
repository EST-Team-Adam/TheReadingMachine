import re
from nltk.corpus import stopwords
from thereadingmachine.SBD import SBD                                        # Sentence Boundary Definition and some preliminary cleaning
from thereadingmachine.sentence_keywords import sentence_keywords
from nltk.stem.snowball import SnowballStemmer
from thereadingmachine.sentiment_VADER import VADER2
from thereadingmachine.sentiment_GoogleNLP import GoogleNLP2


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
  
  
def wordslist(words_list):                                    # prepares the checkwords set to be used
    stemmer = SnowballStemmer("english")
    checkwords = list()
    checkwords2 = list()   
    for word in words_list:                            # takes single words from extracted keywords
        checkwords.append(re.findall(r"[\w']+|[.,!?;]", word))
    checkwords = set(sum(checkwords,[]))               # set() for avoiding multiple identical words
    checkwords = [word for word in checkwords if word not in stopwords.words('english')]      # stopwords removal
    for word in checkwords:
        checkwords2.append(stemmer.stem(word))
    return checkwords2
    

def sentences_analyzer(tests, checkwords):  
  checkwords = wordslist(checkwords)  
  analyzed_sentences = list()
  for test in tests:
      article_sentences = SBD(test)
      dict = {'sentences':[], 'date':[], 'id':[]}
      if len(keyword_alarm(article_sentences,checkwords))>0:
         dict['date'] = test['date']
         dict['id'] = test['id']
         dict['sentences'] = keyword_alarm(article_sentences,checkwords)   # resulting dict is dict['commodity'][number(article)][sentence]
         analyzed_sentences.append(dict)
  return analyzed_sentences