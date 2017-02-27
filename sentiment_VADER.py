from thereadingmachine.VADER.vaderSentiment import SentimentIntensityAnalyzer

def VADER(article_sentences):
    analyzer = SentimentIntensityAnalyzer()
    sentiment = list()
    for sentence in article_sentences:
       vs = {}
       vs = analyzer.polarity_scores(sentence)
       sentiment.append(vs)
    return sentiment