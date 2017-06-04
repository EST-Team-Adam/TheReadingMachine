from thereadingmachine.sentence_keywords import sentence_keywords


def article_keywords(article_sentences):
    results_article = list()
    for sentence in article_sentences:
        #if __name__ == '__main__':
            #result_article = sentence_keywords(sentence)
            results_article.append(sentence_keywords(sentence))
    return results_article
