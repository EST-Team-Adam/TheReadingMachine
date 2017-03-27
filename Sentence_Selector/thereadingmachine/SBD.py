from nltk.tokenize import sent_tokenize
from thereadingmachine.textcleaner import textcleaner

# Sentence Boundary Definition
def SBD(test, checkwords):
    names_list = ['Derica','Ray','Condoleeza', 'Miss','Mister','Mr','Ms']                 # Add names here if you want to drop them
    article_sentences = sent_tokenize(textcleaner(test['article']))
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
