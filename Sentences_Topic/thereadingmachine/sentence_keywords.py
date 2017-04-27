from thereadingmachine.sentence_tagger import Topic_Extractor


def sentence_keywords(sentence):
    results = list()
    topic_extractor = Topic_Extractor(sentence)
    results.append(topic_extractor.extract())
    return results