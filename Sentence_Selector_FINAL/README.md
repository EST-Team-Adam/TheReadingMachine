# Sentence Selector #

The script, which is based on Sentence Topics, extracts each sentence main topics and extracts relevant sentences 
for any given named entity. In particular Sentence Topics extracts each sentence main topics (namely the Noun Phrases) in the form 
of a set of keywords, therefore Sentence Selector checks if a set of given words are present in the extracted topics. 
If the given word is present, the sentence is properly formatted (namely cleaned from a few special characters), then 
it's analysed using VADER sentiment analysis tool and Google NLP and the result is stored in a list.
The final output is a JSON file per each named entity, in this version _wheat_, _soybeans_ and _maize_, which contains sentences, sentiment
scores, article id and dates.

## The script ##
The script is based on _TheReadingMachine_ and, using as input the file _"amis_articles_27_11_2016_indexed.jsonl"_, delivers the file
_"amis_articles_27_11_2016_sentences_from_indexed.jsonl"_ as output.

The output contains the same content of the input plus a dictionary of sentences (keys), topic-keywords (dictionary keys) and two sets of sentiment values: VADER extracted sentiment and Google NLP extracted sentiment.

The algorithm is composed by nine files which have been added to _TheReadingMachine_: the main script _"Sentence_Topic_POC.py"_ and the auxiliary scripts _sentence_selector.py_, _"SBD.py"_, _"textcleaner.py"_, _"sentence_tagger.py"_, _"sentence_keywords.py"_, _"article_keywords.py"_, _"sentiment_VADER.py"_ and _"sentiment_GoogleNLP.py"_. The tenth file contained in _thereadingmachine_ is _keyword.py_ created by Michael Kao.

_"Sentence_Topic_POC.py"_ is the main script: it loads the modules, loads the two functions needed for topic-keywords extraction, loads
the articles and runs the analysis. Once the topic-keywords are extracted, they are incorporated into the article corpus sentence by sentence and the whole output is then written into a new JSONL file.

_"Sentence_Selector.py"_ is the script which contains the three script main functions: _keyword_alarm_, _wordslist_ and _sentences_analyzer_.

The function _wordslist_ is connected to Michael Kao's extracted keywords and gives the checkwords that the program will look for. Given the structure of the whole algorithm, a few of these keywords have been dropped in order to avoid too general sentences.

The function _keyword_alarm_ checks if a topic-keyword extracted from the extractor is mirrored in the elaborated commodities keywords: if it is, the sentence is stored.

The function _sentences_analyzer_ takes the sentences from _keyword_alarm_ and, using both VADER and Google NLP, extracts the sentiment and stores all the results (article id, date, sentences, sentiments) in an output that will be converted in a JSON file. This function is the most important, given the fact that uses all the others.

_"SBD.py"_ and _"textcleaner.py"_ are auxiliary scripts in _TheReadingMachine_ which define each sentence boundaries and clean each article from few special characters (as /r) and a few french words which prevented the use of Google NLP for sentiment extraction. 
Given the fact that the word _"Rice"_ can be either the commodity or a surname, this part of the script drops the sentences in which the word _Rice_ appears as a surname. Obviously the script in written following a flexible approach, therefore it checks for any given commodity name if it's used as a surname for any given sentence.

_"sentence_keywords.py"_, _"article_keywords.py"_ and _"sentence_tagger.py"_ contain the tagger and the keyword-topic extractor. In particular _sentence_tagger.py_ contains the tagger and trains it on the brown corpus, while _"sentence_keywords.py"_ extracts each sentence keywords and _"article_keywords.py"_ extracts all the keywords from each article sentence.

_"sentiment_VADER.py"_ and _"sentiment_GoogleNLP.py"_ extract sentiment from each sentence. Unfortunately GoogleNLP reaches the maximum amount of requests when run on the whole articles corpus.

## The Input ##
Script inputs are: _amis_articles_27_11_2016_indexed.jsonl_ and _key.py_.

_amis_articles_27_11_2016_indexed.jsonl_ contains 140971 indexed articles. The version of this file can be changed and there shouldn't be problems.

_key.py_ is Michael Kao keywords extracting script. It gives back _wheat_keywords_, _rice_keywords_, _maize_keywords_, _barley_keywords_, _soybean_keywords_ and _grain_keywords_ that are then used to select the sentences.

## The Output ##
