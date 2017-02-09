from nltk.tokenize import sent_tokenize

# Sentence Boundary Definition
def SBD(test):
    #test = test.replace('\r', ' ')
    article_sentences = sent_tokenize(test['article'])
    return article_sentences