
# Sentence Topics #

The algorithm performs Part Of Speech analysis using a bigram tagger and extracts each sentence main topics in form of a set of keywords.
More information about the algorithm can be found in the file _"Sentence_Topic.doc"_

### The Script ###
The script is based on _TheReadingMachine_ and, using as input the file _"amis_articles_27_11_2016_indexed.jsonl"_, delivers the file
_"amis_articles_27_11_2016_sentences_from_indexed.jsonl"_ as output.

The output contains the same content of the input plus a dictionary of sentences (keys), topic-keywords (dictionary keys) and two sets of sentiment values: VADER extracted sentiment and Google NLP extracted sentiment.
For test purposes the set of articles is constrained to a sample of 1000 articles, but the script works for all the articles corpus: full analysis 
can be performed by setting _tests = articles_ (line 40) in the main file named _"Sentence_Topic_POC.py"_.

The algorithm is composed by nine files which have been added to _TheReadingMachine_: the main script _"Sentence_Topic_POC.py"_ and the auxiliary scripts _sentence_selector.py_, _"SBD.py"_, _"textcleaner.py"_, _"sentence_tagger.py"_, _"sentence_keywords.py"_, _"article_keywords.py"_, _"sentiment_VADER.py"_ and _"sentiment_GoogleNLP.py"_.

_"Sentence_Topic_POC.py"_ is the main script: it loads the modules, loads the two functions needed for topic-keywords extraction, loads
the articles and runs the analysis. Once the topic-keywords are extracted, they are incorporated into the article corpus sentence by sentence and the whole output is then written into a new JSONL file.

_"Sentence_Selector.py"_ is the script which contains the three script main functions: _keyword_alarm_, _wordslist_ and _sentences_analyzer_.

The function _wordslist_ is connected to Michael Kao's extracted keywords and gives the checkwords that the program will look for. Given the structure of the whole algorithm, a few of these keywords have been dropped in order to avoid too general sentences. In other words let's consider the following example:

_"Brown rice imports are up as brown rice is still present in the list"_

In this sentence I'll have as Noun Phrases extracted by the keyword-topic extractor the set _['Brown', 'rice imports', 'brown rice']_ and in the set of Rice keywords I've _[brown rice]_. For how the script is built, it will separately check if the words _[brown]_ and _[rice]_ are present in the set _['brown', 'rice', 'imports']_ and, given the presence of either _[rice]_ and _[brown]_, it will store and analyze the sentence. If we had the same sentence, but we had _[leaves]_ instead of _[rice]_, the algorithm would have stored and analyzed the sentence anyway given the presence of the only word _[brown]_. In order to avoid this, all the misleading commodity keywords composed by the couple _[adjective + commodity]_ have been restricted to just _[commodity]_. All the others commodities peculiar names have been mantained.

The function _keyword_alarm_ checks if a topic-keyword extracted from the extractor is mirrored in the elaborated commodities keywords: if it is, the sentence is stored.

The function _sentences_analyzer_ takes the sentences from _keyword_alarm_ and, using both VADER and Google NLP, extracts the sentiment and stores all the results (article id, date, sentences, sentiments) in an output that will be converted in a JSON file. This function is the most important, given the fact that uses all the others.

_"SBD.py"_ and _"textcleaner.py"_ are auxiliary scripts in _TheReadingMachine_ which define each sentence boundaries and clean each article from few special characters (as /r) and a few french words which prevented the use of Google NLP for sentiment extraction. 
Given the fact that the word _"Rice"_ can be either the commodity or a surname, this part of the script drops the sentences in which the word _Rice_ appears as a surname. Obviously the script in written following a flexible approach, therefore it checks for any given commodity name if it's used as a surname for any given sentence. At the moment the list of names for which the sentence is dropped out is:

_['Derica','Ray','Condoleeza', 'Miss','Mister','Mr','Ms']_

_"sentence_keywords.py"_, _"article_keywords.py"_ and _"sentence_tagger.py"_ contain the tagger and the keyword-topic extractor. In particular _sentence_tagger.py_ contains the tagger and trains it on the brown corpus, while _"sentence_keywords.py"_ extracts each sentence keywords and _"article_keywords.py"_ extracts all the keywords from each article sentence.

_"sentiment_VADER.py"_ and _"sentiment_GoogleNLP.py"_ extract sentiment from each sentence. Unfortunately GoogleNLP reaches the maximum amount of requests when run on the whole articles corpus.

### Proof Of Concept ###

Let's imagine that I've two text blocks:

_"Miss Rice went to South Africa last week. Condoleeza Rice said good stuff about american government. I can also talk about Mr Rice who actually won a competition."_

_"Kenya rice production is getting better and better. Paddy is increasing for 2$ and that's enough for being accounted. In US rice price is increased by 20$. Brown rice imports are getting lower as brown rice is still present in the list."_

The first one has Rice used as a name, while the second one has rice used as a commodity.

By passing these two sets in the _sentences_analyzer_ function I'll get as result:
_[{'date': u'2014-06-10 00:00:00', 'id': u'a00069366', 'sentences': [('Kenya rice production is getting better and better.', {'neg': 0.0, 'neu': 0.508, 'pos': 0.492, 'compound': 0.7003}), ('Paddy is increasing for 2$ and that  enough for being accounted.', {'neg': 0.0, 'neu': 1.0, 'pos': 0.0, 'compound': 0.0}), ('In US rice price is increased by 20$.', {'neg': 0.0, 'neu': 0.769, 'pos': 0.231, 'compound': 0.2732}), ('Brown rice imports are getting lower as brown rice is still present in the list.', {'neg': 0.136, 'neu': 0.864, 'pos': 0.0, 'compound': -0.296})]}]_

Therefore for this set all the sentences dealing with rice as commodity have been selected, while all the sentences dealing with Rice as surname have been dropped out.

### Next Research Topics ###

As for this same script refinement, different settings for the Context Free Grammar will be tested in order to extrapolate just
futere tense sentences.
