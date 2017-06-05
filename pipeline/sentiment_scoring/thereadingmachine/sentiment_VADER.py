from VADER.vaderSentiment import SentimentIntensityAnalyzer

# for the analysis of all the sentences in an article


def VADER(article_sentences):
    analyzer = SentimentIntensityAnalyzer()
    sentiment = list()
    for sentence in article_sentences:
        vs = {}
        vs = analyzer.polarity_scores(sentence)
        sentiment.append(vs)
    return sentiment

# for the analysis of just one sentence


def VADER2(sentence):
    analyzer = SentimentIntensityAnalyzer()
    sentiment = analyzer.polarity_scores(sentence)
    return sentiment
