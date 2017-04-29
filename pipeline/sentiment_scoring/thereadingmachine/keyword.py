import re
from nltk.corpus import wordnet as wn


# The topic and key word functions assumes that we know the topics
# already. For example, wheat, rice and soybean related topic.


def get_topic_keywords(topic):
    '''This function takes a a topic as a single character and returns
    keywords in the WordNet that are relevant.

    Relevancy is defined in the sense of hypernym, hyponym, meronym
    and holonyms.

    It is important to note that WordNet

    '''

    synsets = wn.synsets(topic)
    # NOTE (Michael): Need to think the level of synsets we need to
    #                 iterate.

    # Get hypernym synsets.
    # hypernym_synsets = []
    # [hypernym_synsets.extend(synset.hypernyms()) for synset in synsets]

    # Get hyponym synsets.
    hyponym_synsets = []
    [hyponym_synsets.extend(synset.hyponyms()) for synset in synsets]

    # Get part meronym synsets, part meronym are compmonents of the
    # object.
    part_meronyms_synsets = []
    [hyponym_synsets.extend(synset.part_meronyms())
     for synset in synsets]

    # Get substance meronym synsets, substance meronym are materials
    # of the object.
    substance_meronyms_synsets = []
    [hyponym_synsets.extend(synset.substance_meronyms())
     for synset in synsets]

    # Add the set together
    complete_synsets = hyponym_synsets + \
        part_meronyms_synsets + substance_meronyms_synsets

    # Extract keywords of the synsets.
    keywords = [topic]
    [keywords.extend(hyponym_synset.lemma_names())
     for hyponym_synset in complete_synsets]
    # NOTE (Michael): Porbably need to repalace '_' with space annd
    #                 try to match with collocation.
    keywords = [re.sub('_', ' ', keyword) for keyword in keywords]
    return keywords


def extract_text_keywords(text, topic):
    '''This function takes a text and identifies keywords in the text
    that are related to a given topic.

    '''

    keywords = get_topic_keywords(topic)
    # located_keywords = set([word
    #                         for word in text
    #                         if word in keywords])
    located_keywords = set([word
                            for word in keywords
                            if word in text])
    return {topic: located_keywords}


def tag_commodity(article, wheat_keywords, rice_keywords,
                  maize_keywords, soybean_keywords,
                  grain_keywords):
    keyword = {'hasWheat': 0,
               'hasRice': 0,
               'hasMaize': 0,
               'hasSoybean': 0,
               'hasGrain': 0
               }

    wheat_match = set(wheat_keywords).intersection(
        article['processed_article'])
    rice_match = set(rice_keywords).intersection(
        article['processed_article'])
    maize_match = set(maize_keywords).intersection(
        article['processed_article'])
    soybean_match = set(soybean_keywords).intersection(
        article['processed_article'])
    grain_match = set(grain_keywords).intersection(
        article['processed_article'])

    if len(wheat_match) > 0:
        keyword['hasWheat'] = 1
    if len(rice_match) > 0:
        keyword['hasRice'] = 1
    if len(maize_match) > 0:
        keyword['hasMaize'] = 1
    if len(soybean_match) > 0:
        keyword['hasSoybean'] = 1
    if len(grain_match) > 0:
        keyword['hasGrain'] = 1
    return keyword


def get_amis_topic_keywords():
    # Pre define the topics
    topics = ['wheat', 'rice', 'maize', 'barley', 'soybean']
    wheat_keywords, rice_keywords, maize_keywords, barley_keywords, soybean_keywords = [
        get_topic_keywords(topic) for topic in topics]
    grain_keywords = list(set(get_topic_keywords('grains')) -
                          set(wheat_keywords) -
                          set(rice_keywords) -
                          set(maize_keywords) -
                          set(soybean_keywords) -
                          set(barley_keywords))
    # Manually remove keywords
    for index, grain in enumerate(grain_keywords):
        for topic, topic_keyword in zip(topics,
                                        [wheat_keywords, rice_keywords,
                                         maize_keywords,
                                         soybean_keywords]):
            search_string = r'\b' + re.escape(topic) + r'\b'
            if bool(re.search(search_string, grain)):
                print('popping out ' + (grain))
                topic_keyword.append(grain_keywords.pop(index))

    return wheat_keywords, rice_keywords, maize_keywords, barley_keywords, soybean_keywords, grain_keywords
