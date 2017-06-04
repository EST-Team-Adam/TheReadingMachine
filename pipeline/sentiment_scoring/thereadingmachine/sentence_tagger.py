import nltk
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
from nltk.corpus import brown

## SENTENCE TOPIC EXTRACTION ##

# POS Tagger
train_corpus = brown.tagged_sents(categories='news')
tagger = nltk.RegexpTagger(
    [(r'^-?[0-9]+(.[0-9]+)?$', 'CD'),                      # CD : Cardinal Number
     (r'(-|:|;)$', ':'),                                   # : : Sign
     (r'\'*$', 'MD'),                                      # MD : Modal
     (r'(The|the|A|a|An|an)$', 'AT'),                      # AT : Article
     (r'(.*able|.*al|.*ful|.*ish)$', 'JJ'),                # JJ : Adjective
     (r'^[A-Z].*$', 'NNP'),                                # NNP : Proper Noun, singular (capital letters)
     (r'(.*ness|.*e)$', 'NN'),                             # NN : Noun, singular or mass
     (r'.*ly$', 'RB'),                                     # RB : Adverb
     (r'.*s$', 'NNS'),                                     # NNS : Noun Plural
     (r'.*ing$', 'VBG'),                                   # VBG : Verb, gerund or present participle
     (r'.*ed$', 'VBD'),                                    # VBD : Verb, past tense (may be useful to add a new category for future)
     (r'.*', 'NN')                                         # NN : Noun, singular or mass
])
unigram = nltk.UnigramTagger(train_corpus, backoff=tagger)
bigram = nltk.BigramTagger(train_corpus, backoff=unigram)

# semi-CFG (defines the tag)
cfg = {}
cfg["NNP+NNP"] = "NNP"
cfg["NN+NN"] = "NNI"                     # NNI: Noun, Singular Common
cfg["NNI+NN"] = "NNI"
cfg["JJ+JJ"] = "JJ"
cfg["JJ+NN"] = "NNI"
cfg["NNI+VBG"] = "NNI"                   # This line indicates the bigram word-verb in the present
cfg["NNI+VBD"] = "NNI"                   # by changing this line should be possible to drop past tense sentences (to be tested)

class Topic_Extractor(object):
    def __init__(self, sentence):
        self.sentence = sentence
    # Sentence Tokenization
    def sentence_tokens(self, sentence):
        tokens = nltk.word_tokenize(sentence)
        return tokens
    # Normalize brown corpus' tags ("NN", "NN-PL", "NNS" > "NN")
    def normalization(self, tagged):
        n_tagged = []
        for t in tagged:
            if t[1] == "NP-TL" or t[1] == "NP":
                n_tagged.append((t[0], "NNP"))
                continue
            if t[1].endswith("-TL"):
                n_tagged.append((t[0], t[1][:-3]))
                continue
            if t[1].endswith("S"):
                n_tagged.append((t[0], t[1][:-1]))
                continue
            n_tagged.append((t[0], t[1]))
        return n_tagged
    # Extract the main topics from the sentence
    def extract(self):
        tokens = self.sentence_tokens(self.sentence)
        tags = self.normalization(bigram.tag(tokens))
        merge = True
        while merge:
            merge = False
            for x in range(0, len(tags) - 1):
                t1 = tags[x]
                t2 = tags[x + 1]
                key = "%s+%s" % (t1[1], t2[1])
                value = cfg.get(key, '')
                if value:
                    merge = True
                    tags.pop(x)
                    tags.pop(x)
                    match = "%s %s" % (t1[0], t2[0])
                    pos = value
                    tags.insert(x, (match, pos))
                    break
        matches = []
        for t in tags:
            if t[1] == "NNP" or t[1] == "NNI":
            #if t[1] == "NNP" or t[1] == "NNI" or t[1] == "NN":
                matches.append(t[0])
        return matches