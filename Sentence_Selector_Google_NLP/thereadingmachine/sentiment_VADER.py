from thereadingmachine.VADER.vaderSentiment import SentimentIntensityAnalyzer

def VADER(article_sentences):                      # for the analysis of all the sentences in an article
    analyzer = SentimentIntensityAnalyzer()
    sentiment = list()
    for sentence in article_sentences:
       vs = {}
       vs = analyzer.polarity_scores(sentence)
       sentiment.append(vs)
    return sentiment
        
    
def VADER2(sentence):                              # for the analysis of just one sentence
    analyzer = SentimentIntensityAnalyzer()
    sentiment = analyzer.polarity_scores(sentence)
    return sentiment