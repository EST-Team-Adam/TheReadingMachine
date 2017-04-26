from __future__ import division
from math import log
from inspect import getsourcefile
from os.path import abspath, join, dirname
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk import ngrams
from collections import Counter
from thereadingmachine.word_counter import convert



def read_lexicon(lexicon_file):                  # reads the lexicon
    lex_dict = {}
    with open(lexicon_file) as f:
         lexicon_full = f.read()
    for line in lexicon_full.split('\n'):
        (word, measure) = line.strip().split('\t')[0:2]
        lex_dict[word] = float(measure)
    return lex_dict
    
    
    
    
def contexts_extractor(sentences, selected_words):      # defines the context of each selected word from the same sentences
    contexts_dic = {}
    contexts = list()
    trigrams = list()
    word_i = list()
    words_i = {}
    for sentence in sentences:               # trigram extraction
        for sentence in sentence:
            trigrams.append(list(ngrams(word_tokenize(convert(sentence['sentences'][0][0])),3)))   # remove stopwords? maybe it's the case
    flatten = lambda l: [item for sublist in trigrams for item in sublist]
    trigrams = flatten(trigrams)
    for word in selected_words:              # context extraction
        selected_trigrams = list()
        context1 = list()
        context = list()
        selected_trigrams.append([trigram for trigram in trigrams if word in trigram])   # selects the trigrams which contain a word in the selected_words
        selected_trigrams = selected_trigrams[0]
        word_i.append(len(selected_trigrams))                                    # counter of how many times the word to be added appears in the trigrams
        for trigram in selected_trigrams:
            #for trigram in trigram:
            trigram = list(trigram)
            trigram.remove(word)                               # removes the word of selected_words, leaving the context
            context1.append(trigram)
        flatten = lambda l: [item for sublist in context1 for item in sublist]
        context = flatten(trigrams)
        contexts_dic[word] = dict(Counter(context))
    words_i = dict(zip(selected_words, word_i))
    #words_i = [word for word in words_i if word not in stopwords.words('english')]   # stopwords removal
    #words_i = [word for word in words_i if not any(c.isdigit() for c in word)]
    #contexts_dic = [word for word in words_i if word not in stopwords.words('english')]   # stopwords removal
    #contexts_dic = [word for word in words_i if not any(c.isdigit() for c in word)]
    contexts = [contexts_dic, words_i]                               # list which contains a dictionary per context of word_i and a counter of word_i occurrences in selected_trigrams 
    contexts = contexts
    return contexts
    
    
    
def pointwise_mutual_information(wordfreq, contexts):
    n = sum(wordfreq.values())
    words = list()
    PMI = {}
    a = list()
    b = list()
    for i in contexts[0]:
        PMI_selected_word = list()
        word_i = list()
        words_j = list()
    #print i, contexts[0][i]
        word_i = i
        words_j = contexts[0][i]
        a.append(i)
        for word in words_j:                             # word is word_j!
            PMI_selected_word.append([log(((contexts[1][word_i]*n)/(wordfreq[word_i]*(wordfreq[word])))), word])
        b.append(PMI_selected_word)
        PMI = dict(zip(a,b))
    return PMI
    
    
    
