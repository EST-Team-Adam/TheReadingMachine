from nltk.tokenize import sent_tokenize
from thereadingmachine.textcleaner import textcleaner

# Sentence Boundary Definition
def SBD(test):
    article_sentences = sent_tokenize(textcleaner(test['article']))
    return article_sentences
