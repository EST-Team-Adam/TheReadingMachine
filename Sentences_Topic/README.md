
#Sentence Topics#

The algorithm performs Part Of Speech analysis using a bigram tagger and extracts each sentence main topics in form of a set of keywords.
More information about the algorithm can be found in the file _"Sentence_Topic.doc"_

###The Script###
The script is based on _TheReadingMachine_ and, using as input the file _"amis_articles_27_11_2016_indexed.jsonl"_, delivers the file
_"amis_articles_27_11_2016_sentences_from_indexed.jsonl"_ as output.

The output contains the same content of the input plus a dictionary of sentences (keys) and topic-keywords (values) extracted from the same sentences.
For test purposes the set of articles is constrained to two articles, but the script works for all the articles corpus: full analysis 
can be performed by setting _tests = articles_ (line 40) in the main file named _"Sentence_Topic_POC.py"_.

The algorithm is composed by three files which have been added to _TheReadingMachine_: the main script _"Sentence_Topic_POC.py"_,  
_"SBD.py"_ and _"sentence_tagger.py"_.

_"Sentence_Topic_POC.py"_ is the main script: it loads the modules, loads the two functions needed for topic-keywords extraction, loads
the articles and runs the analysis. Once the topic-keywords are extracted, they are incorporated into the article corpus sentence by sentence
and the whole output is then written into a new JSONL file.

_"SBD.py"_ is the auxiliary script in _TheReadingMachine_ which defines each sentence boundaries.

_"sentence_tagger.py"_ contains the tagger and the keyword-topic extractor.

###Next Research Topics###

Next objective is to build a sentence extraction algorithm which relies only on the topic-keywords extracted by sentence topics
algorithm: such words will be compared to the commodities keywords already extracted. In this way a sharper sentence selection 
should be achievable as sentences will be extracted for different commodities and different contexts.

As for this same script refinement, different settings for the Context Free Grammar will be tested in order to extrapolate just
futere tense sentences.
