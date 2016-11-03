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
    hypernym_synsets = []
    [hypernym_synsets.extend(synset.hypernyms()) for synset in synsets]

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
    complete_synsets = hypernym_synsets + hyponym_synsets + \
        part_meronyms_synsets + substance_meronyms_synsets

    # Extract keywords of the synsets.
    keywords = []
    [keywords.extend(hyponym_synset.lemma_names())
     for hyponym_synset in complete_synsets]
    # NOTE (Michael): Porbably need to repalace '_' with space annd
    #                 try to match with collocation.
    return keywords


def extract_text_keywords(text, topic):
    '''This function takes a text and identifies keywords in the text
    that are related to a given topic.

    '''

    keywords = get_topic_keywords(topic)
    located_keywords = set([word
                            for word in text
                            if word in keywords])
    return located_keywords
