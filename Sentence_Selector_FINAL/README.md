# Sentence Selector & Sentiment Extraction #

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

_"sentence_keywords.py"_, _"article_keywords.py"_ and _"sentence_tagger.py"_ contain the tagger and the keyword-topic extractor. In particular _sentence_tagger.py_ contains the tagger and trains it on the Brown Corpus, while _"sentence_keywords.py"_ extracts each sentence keywords and _"article_keywords.py"_ extracts all the keywords from each article sentence.

_"sentiment_VADER.py"_ and _"sentiment_GoogleNLP.py"_ extract sentiment from each sentence. Unfortunately GoogleNLP reaches the maximum amount of requests when run on the whole articles corpus, but it can be re-activated by modifying the file _"sentence_selector.py"_ lines 30 and 31. In particular for Google NLP reactivation those lines should be as follows:

_(line 30) sentiment_Google.append(GoogleNLP2(sentence))_

_(line 31) selected_sentences = zip(selection, sentiment_VADER, sentiment_Google)_

## The Input ##
Script inputs are: _amis_articles_27_11_2016_indexed.jsonl_ and _key.py_.

_amis_articles_27_11_2016_indexed.jsonl_ contains 140971 indexed articles. The version of this file can be changed and there shouldn't be problems.

_key.py_ is Michael Kao keywords extracting script. It gives back _wheat_keywords_, _rice_keywords_, _maize_keywords_, _barley_keywords_, _soybean_keywords_ and _grain_keywords_ that are then used to select the sentences.

## The Output ##
The output is a list of sentences and extracted sentiment per each commodity. In particular supported commodities are wheat (11341 sentences), rice (1549 sentences), soybeans (9440 sentences), maize (440 sentences), barley (732 sentences) and grains (3232 sentences).
In particular each commodity list of sentences is a list of dictionaries and each dictionary is composed by _date_, _article_id_, _sentences_ and _sentiment_ (positive, neutral, negative and compound).

Each list is then dumped into a JSON file, named for example

_amis_articles_27_11_2016_sentences_wheat.jsonl_ 

The complete list of output files is

_amis_articles_27_11_2016_sentences_wheat.jsonl_ 

_amis_articles_27_11_2016_sentences_rice.jsonl_ 

_amis_articles_27_11_2016_sentences_soybeans.jsonl_ 

_amis_articles_27_11_2016_sentences_maize.jsonl_ 

_amis_articles_27_11_2016_sentences_barley.jsonl_ 

_amis_articles_27_11_2016_sentences_grain.jsonl_ 

## How to call the main functions ##

The two main functions are _sentences_analyzer(sentence)_ and _SBD(articles, checkwords)_: the first finds in a sentence the Noun Phrases (namely the topics), while the other divides the text into sentences and filters them by given checkwords. To call them run _selector_POC.py_ until line 33, then just load the modules

_from thereadingmachine.SBD import SBD_

_from thereadingmachine.sentence_keywords import sentence_keywords_


and then call them using

_tests = articles_    # articles loaded from input file_

_tests[0]['article'] = "Miss Rice went to South Africa last week. Condoleeza Rice said good stuff about american government. I can also talk about Mr Rice who actually won a competition."_

_tests[1]['article'] = "Kenya rice production is getting better and better. Paddy is increasing for 2$ and that's enough for being accounted. In US rice price is increased by 20$. Brown rice imports are getting lower as brown rice is still present in the list."_

_commodity = ['rice']_

_checkwords = commodity + wordslist(rice_keywords)_

_SBD(tests[1],checkwords)   # can be also tests[0]_

_sentence_keywords(SBD(tests[1],checkwords)[0])   # _sentence_keywords(.)[i] where i is the sentence index_

or in a more free way

_sentence_keywords('It is always nice to write test sentences')_

The expected results are:

_SBD(tests[1],checkwords) = ['Kenya rice production is getting better and better.', 'Paddy is increasing for 2$ and that  enough for being accounted.', 'In US rice price is increased by 20$.', 'Brown rice imports are getting lower as brown rice is still present in the list.']_

_SBD(tests[0],checkwords) = []_

_sentence_keywords(SBD(tests[1],checkwords)[0]) = ['Kenya', 'rice production']_

_sentence_keywords(SBD(tests[1],checkwords)[3]) = ['Brown', 'rice imports', 'brown rice']_

## Breaking down the topic-keywords extraction ##

Sentence Topics extraction relies on Part Of Speech tagging, namely the recognition of each word role in the sentence: words will be labeled as nouns, verbs et cetera depending on their logical function. Obviously the algorithm is not that straightforward, because it relies on a tagged corpora, from which are then trained other taggers.

NLTK comes with a few tagged corpora, namely a dictionary of words and respective logical function labels. By the way tagged words cannot be used into sentence topics extraction because, by using just a dictionary of tagged words, each word logical function will be insensitive of the word role in the sentence.

In order to avoid this the algorithm works using the tagged sentences corpus from the Brown corpus. 
First of all a Regular Expression Tagger is built using a list of words of suffixes which give to each word its function label, namely common noun, verb, adjective et cetera. The RE tagger first tries on the word all the possible labels then, as a residual option if no labels fit, at last assigns the label “Noun”.

Then a Unigram tagger is trained on the same corpus using the Regular Expression Tagger as backoff. A Unigram tagger is a tagger that still doesn’t evaluate the role of the word in the sentence, but just gives to the word the most probable label where probabilities are defined using the corpus.

As last preliminary step a Bigram tagger is trained using the same Brown corpus and the Unigram tagger as backoff. The Bigram tagger considers words in pairs when assigns the labels, therefore they are given depending on the (small) context defined by the words pair.
Once the words are labeled depending on their logical function, A Context Free Grammar is defined: in the CFG a few of the possible interactions between the words are modeled. In particular the interactions involving singular and plural common nouns, proper nouns and the interaction between adjectives and nouns are modeled.

The Topic Extractor then selects the topics: if both the bigram words are labeled as proper noun or common noun, then the first noun word of the bigram is selected as label. If a pair composed by adjective and noun is selected, then it’is reported as topic. There are many different cases and, to the basic algorithm, also verbs have been applied to the Context Free Grammar.

In particular the interactions between verbs and nouns can be tested, because it should be possible to isolate future tense sentences by modeling verbs and modals or change extracted extracted topic-keywords by modifying the Context Free Grammar.
