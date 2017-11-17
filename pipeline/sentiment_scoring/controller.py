import warnings
from pandas import DataFrame
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


def article_sentiment_scoring(articles, article_col, id_col, date_col, method,
                              to_df=True):
    scored_articles = list()
    analyser = SentimentIntensityAnalyzer()
    for article in articles:
        score = dict()
        if 'VADER' in method:
            article_score = analyser.polarity_scores(article[article_col])
            article_score['compound_sentiment'] = article_score.pop('compound')
            article_score['positive_sentiment'] = article_score.pop('pos')
            article_score['neutral_sentiment'] = article_score.pop('neu')
            article_score['negative_sentiment'] = article_score.pop('neg')
            article_score.update({id_col: article.get(id_col),
                                  date_col: article.get(date_col)})
            score.update(article_score)
        if 'GOOGLE_NLP' in method:
            warnings.warn('Google NLP method not yet implemented')
        scored_articles.append(score)
    if to_df:
        scored_articles = DataFrame(scored_articles)
    return scored_articles
