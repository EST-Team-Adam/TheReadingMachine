
#Sentence Topics#

The algorithm performs Part Of Speech analysis using a bigram tagger and extracts each sentence main topics in form of a set of keywords.
More information about the algorithm can be found in the file _"Sentence_Topic.doc"_

###The Script###
The script is based on _TheReadingMachine_ and, using as input the file _"amis_articles_27_11_2016_indexed.jsonl"_, delivers the file
_"amis_articles_27_11_2016_sentences_from_indexed.jsonl"_ as output.

The output contains the same content of the input plus a dictionary of sentences (keys), topic-keywords (dictionary keys) and two sets of sentiment values: VADER extracted sentiment and Google NLP extracted sentiment.
For test purposes the set of articles is constrained to two articles, but the script works for all the articles corpus: full analysis 
can be performed by setting _tests = articles_ (line 40) in the main file named _"Sentence_Topic_POC.py"_.

The algorithm is composed by eight files which have been added to _TheReadingMachine_: the main script _"Sentence_Topic_POC.py"_ and the auxiliary scripts _"SBD.py"_, _"textcleaner.py"_, _"sentence_tagger.py"_, _"sentence_keywords.py"_, _"article_keywords.py"_, _"sentiment_VADER.py"_ and _"sentiment_GoogleNLP.py"_.

_"Sentence_Topic_POC.py"_ is the main script: it loads the modules, loads the two functions needed for topic-keywords extraction, loads
the articles and runs the analysis. Once the topic-keywords are extracted, they are incorporated into the article corpus sentence by sentence and the whole output is then written into a new JSONL file.

_"SBD.py"_ and _"textcleaner.py"_ are auxiliary scripts in _TheReadingMachine_ which define each sentence boundaries and clean each article from few special characters (as /r) and a few french words which prevented the use of Google NLP for sentiment extraction.

_"sentence_keywords.py"_, _"article_keywords.py"_ and _"sentence_tagger.py"_ contain the tagger and the keyword-topic extractor. In particular _sentence_tagger.py_ contains the tagger and trains it on the brown corpus, while _"sentence_keywords.py"_ extracts each sentence keywords and _"article_keywords.py"_ extracts all the keywords from each article sentence.

_"sentiment_VADER.py"_ and _"sentiment_GoogleNLP.py"_ extract sentiment from each sentence. Unfortunately GoogleNLP reaches the maximum amount of requests when run on the whole articles corpus.

###Next Research Topics###

Next objective is to build a sentence extraction algorithm which relies only on the topic-keywords extracted by sentence topics
algorithm: such words will be compared to the commodities keywords already extracted. In this way a sharper sentence selection 
should be achievable as sentences will be extracted for different commodities and different contexts.

As for this same script refinement, different settings for the Context Free Grammar will be tested in order to extrapolate just
futere tense sentences.
