from __future__ import division
from google_ngram_downloader import readline_google_store
from nltk import word_tokenize
from nltk.corpus import stopwords
import collections
import urllib2
import csv
import urllib
from cookielib import CookieJar


cj = CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))  # for avoiding error 302 when counting the words using google ngrams from too many sentences WORK IN PROGRESS
urllib2.install_opener(opener) 

#def ngramscounter_google(word):                      # access to the google ngram library
#    count = 0
#    fname, url, records = next(readline_google_store(ngram_len=1, indices=word[0]))
#    try:
#	    record = next(records)
#	    while record.ngram != word:
#		    record = next(records)
#	    while record.ngram == word:
#		    count = count + record.match_count
#		    record = next(records)	
#		    print count	
#    except StopIteration:
#	    pass
#    return count
    


def load_total_counts(corpus_id, start_year, end_year):     # total_counts = load_total_counts(corpus_id = 15, start_year=1995, end_year=2005), loads the total count of words in google ngrams
    id_to_url= {
    15: 'http://storage.googleapis.com/books/ngrams/books/googlebooks-eng-all-totalcounts-20120701.txt',
    17: 'http://storage.googleapis.com/books/ngrams/books/googlebooks-eng-us-all-totalcounts-20120701.txt',
    18: 'http://storage.googleapis.com/books/ngrams/books/googlebooks-eng-gb-all-totalcounts-20120701.txt',
    16: 'http://storage.googleapis.com/books/ngrams/books/googlebooks-eng-fiction-all-totalcounts-20120701.txt',
    23: 'http://storage.googleapis.com/books/ngrams/books/googlebooks-chi-sim-all-totalcounts-20120701.txt',
    19: 'http://storage.googleapis.com/books/ngrams/books/googlebooks-fre-all-totalcounts-20120701.txt',
    20: 'http://storage.googleapis.com/books/ngrams/books/googlebooks-ger-all-totalcounts-20120701.txt',
    24: 'http://storage.googleapis.com/books/ngrams/books/googlebooks-heb-all-totalcounts-20120701.txt',
    22: 'http://storage.googleapis.com/books/ngrams/books/googlebooks-ita-all-totalcounts-20120701.txt',
    25: 'http://storage.googleapis.com/books/ngrams/books/googlebooks-rus-all-totalcounts-20120701.txt',
    21: 'http://storage.googleapis.com/books/ngrams/books/googlebooks-spa-all-totalcounts-20120701.txt'
    }
    response = urllib2.urlopen(urllib2.Request(id_to_url[corpus_id]))
    total_counts = []
    data = csv.reader(response, delimiter="\t").next()
    for row in data:
        try:
            year, word_count, _, _ = row.split(',')
            if int(year) >= start_year and int(year) <= end_year:
                total_counts.append(int(word_count))
        except ValueError:
            pass
    return total_counts




def retrieve_absolute_counts(token, corpus, smoothing, start_year, end_year):     # access to the google ngram library alternative
    '''
    This function retrieves the absolute counts for a given token. 
    It first loads the relative frequencies from the ngram viewer and the absolute counts
    for the corpus from Google's source data.
    Then, it multiplies the absolute number of terms in the corpus for any given year with the 
    relative frequency of the search token.
    '''
    corpora = {
        'english' : 15,
        'american english': 17,
        'british english': 18,
        'english fiction': 16,
        'chinese': 23,
        'french': 19,
        'german': 20,
        'hebrew': 24,
        'italian': 22,
        'russian': 25,
        'spanish': 21,
    }
    corpus_id = corpora[corpus]
    token = token.replace(' ', '+')
    url = 'https://books.google.com/ngrams/interactive_chart?content={}&year_start={}&year_end={}' \
             '&corpus={}&smoothing={}'.format(token, start_year, end_year, corpus_id, smoothing)
    page = urllib2.urlopen(urllib2.Request(url)).read()
    start = page.find('var data = ')
    end = page.find('];\n', start)
    data = eval(page[start+12:end])
    frequencies = data['timeseries']
    total_counts = load_total_counts(corpus_id, start_year, end_year)
    absolute_counts = [round(frequencies[i] * total_counts[i]) for i in range(len(frequencies))]
    return absolute_counts


    

def wordcounter(sentences):                            # counter for the sentences set (stopwords removed)
    bag_of_words = list()
    wordfreq = []
    for sentence in sentences:
        for sentence in sentence:
            bag_of_words.append(sentence['sentences'][0][0])
    bag_of_words = ' '.join(bag_of_words)
    tokens = word_tokenize(bag_of_words) 
    tokens = [word for word in tokens if word not in stopwords.words('english')]
    tokens_to_be_looked = list(set(tokens))
    wordcount = [tokens.count(w) for w in tokens_to_be_looked]
    wordfreq = [wordcount , tokens_to_be_looked]
    return wordfreq
    



def wordfreq_to_dic(sentences):                       # gives an absolute values counter dictionary (stopwords included for PMI computation)
    wordfreq_counter = {}
    bag_of_words = list()
    wordfreq = []
    for sentence in sentences:
        for sentence in sentence:
            bag_of_words.append(sentence['sentences'][0][0])
    bag_of_words = ' '.join(bag_of_words)
    tokens = word_tokenize(bag_of_words) 
    tokens_to_be_looked = list(set(tokens))
    wordcount = [tokens.count(w) for w in tokens_to_be_looked]
    wordfreq = [wordcount , tokens_to_be_looked]
    wordfreq = dict(zip(wordfreq[1], wordfreq[0]))
    return wordfreq



def probabilities_sentences(wordfreq):              # computes the probabilities of the sentences set
    p_token = list()
    for word in wordfreq[0]:
        p_token.append(word/len(wordfreq[0]))
    wordfreq = [wordfreq[0], wordfreq[1], p_token]   # just add one column, don't use this
    return wordfreq
    
    
#def probabilities_sentences(wordfreq):              # computes the probabilities of the sentences set
#    p_token = list()
#    for word in wordfreq.values():
#        p_token.append(word/len(wordfreq))
#    wordfreq = [wordfreq[0], wordfreq[1], p_token]   # just add one column, don't use this
#    return wordfreq
    

    
def wordcounter_google(wordfreq):               # counter for google ngram
   counter_google = list()
   for word in wordfreq[1][0:10]:
       type(word.encode('ascii','ignore'))
       word = word.encode('ascii','ignore')
       word = word.lower()
       counter_google.append(retrieve_absolute_counts(word, 'english', smoothing = 0, start_year = 2007, end_year = 2008)[1])
   wordfreq = [wordfreq[0], wordfreq[1], wordfreq[2], counter_google]   # just add one column, don't use this
   return wordfreq
   
   
   
def probabilities_google(wordfreq):            # computes google ngram counter probabilities
    p_token = list()
    for word in wordfreq[3]:
        p_token.append(word/load_total_counts(corpus_id = 15, start_year=2008, end_year=2008)[0])         # relative freq computed using as denominator the number of words in google ngrams in 2008
    wordfreq = [wordfreq[0], wordfreq[1],wordfreq[2], wordfreq[3], p_token]   # just add one column, don't use this
    return wordfreq
    
    
    
def avoid_divide_by_zero(wordfreq):           # avoids to divide by zero when word counter is zero
    wordfreq1 = list()
    for word in wordfreq[4]:
        if (word > 0.0):
           wordfreq1.append(word)
        else:
           word = 0.0000001    # to avoid 'divide by zero' error
           wordfreq1.append(word)
    wordfreq = [wordfreq[0], wordfreq[1],wordfreq[2], wordfreq[3], wordfreq1]
    return wordfreq
    


def convert(selected_words):                         # converts dic unicode in strings
    if isinstance(selected_words, basestring):
        return str(selected_words)
    elif isinstance(selected_words, collections.Mapping):
        return dict(map(convert, selected_words.iteritems()))
    elif isinstance(selected_words, collections.Iterable):
        return type(selected_words)(map(convert, selected_words))
    else:
        return selected_words


    
def words_extraction(sentences, lexicon):
    selected_words = {}
    wordfreq = wordcounter(sentences)
    wordfreq = probabilities_sentences(wordfreq)
    wordfreq = wordcounter_google(wordfreq)  
    wordfreq = [wordfreq[0], wordfreq[1], wordfreq[2], wordfreq[3]]
    wordfreq = probabilities_google(wordfreq)
    wordfreq = avoid_divide_by_zero(wordfreq)
    probabilities = [x/y for x,y in zip(map(float,wordfreq[2]), map(float,wordfreq[4]))]
    extracted_words = dict(zip(wordfreq[1], probabilities))
    selected_words = dict((k, v) for k, v in extracted_words.items() if v >= 1.0)
    selected_words = convert(selected_words)
    for word in selected_words:
        pass
    if any(word in selected_words for selected_words in lexicon):
       selected_words.pop(word, None)
    return selected_words