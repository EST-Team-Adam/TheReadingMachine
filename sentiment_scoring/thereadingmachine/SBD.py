from nltk.tokenize import sent_tokenize
from thereadingmachine.textcleaner import textcleaner
import langid   # drops non-english sentences which create problems with Google NLP

# Sentence Boundary Definition
def SBD(test, checkwords):
    names_list = ['Derica','Ray','Condoleeza', 'Miss','Mister','Mr','Ms']                 # Add names here if you want to drop them
    article_sentences = sent_tokenize(textcleaner(test['article']))
    article_sentences1 = list()
    article_sentences2 = list()
    checkwords1 = checkwords[0].capitalize()
    for article_sentence in article_sentences:                             # iterates over the sentences
        article_sentence = article_sentence.replace(',', '')               # eliminates commas that may confuse the algorithm
        if any(word in article_sentence for word in checkwords1):          # checks if in the sentence there is the checkword
           list_of_words = article_sentence.split()
           if any(word in checkwords1 for word in list_of_words):          # checks if in the sentence there is the checkword
              if (list_of_words[list_of_words.index(checkwords1) -1] for name in names_list):     # check if previous word is a name
                 article_sentence = ''
              else:
                 article_sentence = article_sentence
           article_sentences1.append(article_sentence)
           article_sentences1 = filter(None, article_sentences1) 
    for sentence in article_sentences1:
        if langid.classify(sentence)[0] in ['en']:            # non-english sentences removal for Google NLP
           article_sentences2.append(sentence)
    return article_sentences2
    
    
    
    
# Sentence Boundary Definition for Twitter (unicode issue solved)
def SBD_twitter(test, checkwords):
    names_list = ['Derica','Ray','Condoleeza', 'Miss','Mister','Mr','Ms']                 # Add names here if you want to drop them
    article_sentences = sent_tokenize(textcleaner(unicode(test['article'],errors='ignore')))
    article_sentences1 = list()
    checkwords1 = checkwords[0].capitalize()
    for article_sentence in article_sentences:                             # iterates over the sentences
        article_sentence = article_sentence.replace(',', '')               # eliminates commas that may confuse the algorithm
        if any(word in article_sentence for word in checkwords1):          # checks if in the sentence there is the checkword
           list_of_words = article_sentence.split()
           if any(word in checkwords1 for word in list_of_words):          # checks if in the sentence there is the checkword
              if (list_of_words[list_of_words.index(checkwords1) -1] for name in names_list):     # check if previous word is a name
                 article_sentence = ''
              else:
                 article_sentence = article_sentence
           article_sentences1.append(article_sentence)
           article_sentences1 = filter(None, article_sentences1) 
    return article_sentences1