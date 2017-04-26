# Sentence Selector & Sentiment Extraction #

The script, which is based on Sentence Topics, extracts each sentence main topics and extracts relevant sentences 
for any given named entity. In particular Sentence Topics extracts each sentence main topics (namely the Noun Phrases) in the form 
of a set of keywords, therefore Sentence Selector checks if a set of given words are present in the extracted topics. 
If the given word is present, the sentence is properly formatted (namely cleaned from a few special characters), then 
it's analysed using VADER sentiment analysis tool and Google NLP and the result is stored in a list.
The final output is a JSON file per each named entity, in this version _wheat_, _soybeans_ and _maize_, which contains sentences, sentiment
scores, article id and dates.

## The script ##
The script is based on _TheReadingMachine_ and, using as input the file _"amis_articles_27_11_2016_indexed.jsonl"_, delivers 6 files
_"amis_articles_27_11_2016_sentences_*commodity_name*.jsonl"_ as output.

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
Script inputs are: _amis_articles_27_11_2016_indexed.jsonl_, _twitter_timelines.csv_ and _key.py_.

_amis_articles_27_11_2016_indexed.jsonl_ contains 140971 indexed articles. The version of this file can be changed and there shouldn't be problems.

_twitter_timelines.csv_ contains 203744 different tweets scraped from twitter: these tweets are in different languages, therefore non-english ones are dropped from the analysis because the current dictionary supports just english language.

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

Twitter output is composed by 6 files of english language selected sentences from the tweets with sentiment scores. The files are:

_twitter_tweets_wheat.jsonl_ (2148 tweets)

_twitter_tweets_rice.jsonl_ (377 tweets)

_twitter_tweets_soybeans.jsonl_ (172 tweets)

_twitter_tweets_maize.jsonl_ (63 tweets)

_twitter_tweets_barley.jsonl_ (107 tweets)

_twitter_tweets_grain.jsonl_ (575 tweets)

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

## Twitter Data ##

The analysis of twitter data relies on the Sentences Selector and the data have been adapted to fit its algorithm.

The main script is called _selector_twitter.py_ which relies on _twitter.py_, _sentence_selector.py_ and _keyword.py_ (and the module _json_ for 'dumping' the output). The last important module used is _langid_ for language identification, more info can be found at the following URL: https://github.com/saffsd/langid.py .

_selector_twitter.py_ first reads the twitter data contained in _twitter_timelines.csv_ using the function _twitter_reader_ in _twitter.py_, then calls the function _twitter_formatter_ from _twitter.py_ to adapt twitter data to _sentence_selector.py_ functions, then calls _get_amis_topic_keywords_ from Michael Kao _keyword.py_ for commodity keyword to look for and at the end calls _sentences_analyzer_twitter_ function in _sentence_selector.py_ for sentences selection and sentiment extraction. 

It has to be underlined that while the steps from _get_amis_topic_keywords_ follow the sme path of articles case, there are a few nuisances that have to be underlined in the data formatting part. First of all twitter data fields 'text;;;;;;;;;' and 'created_at' are  respectively substituted with 'article' and 'date' to fit the Sentence Selector algorithm. Then all empty tweets (missing article or date) are dropped out from the analysis. At last _langid_ is used to find english tweets and drop the non-english ones.

When data are correctly formatted they are passed to the a slightly modified version of the sentence selector, namely the function _sentences_analyzer_twitter_ . The only difference with the original _sentences_analyzer_ used in articles is that it relies on a Sentence Boundaries Definer called _SBD_twitter_ that takes care (ignores) unicode special characters which stopped the analysis performed by the articles _SBD_ . This diference can be found in the file _SBD.py_, function _SBD_twitter_ in line 29:

_article_sentences = sent_tokenize(textcleaner(unicode(test['article'],errors='ignore')))_

in particular it's _unicode(test['article'],errors='ignore')_ that in the articles _SBD_ is just _article_sentences = sent_tokenize(textcleaner(test['article']))_ .

The module _langid_ for language recognition can be tested using

_langid.classify("This is a test")_

which will return _('en', -54.41310358047485)_ where the first field is the language.

_langid_ helps in two ways: on one hand by identifying other languages tweets, on the other hand by identifying part of the tweets containing just urls, hashtags et cetera which most of the times do not directly convey any sentiment in their wordings. In the latter case one should open the urls to find and extract the tweet sentiment from there. As a proof:

_langid.classify("#Nutrition https://t.co/s4mP7kG8Ti https://t\xe2\x80\xa6;;;;;;;;', 'id': '695564581364703232', 'screen_name': 'FAOstatistics'}_

returns _('da', -14.586467266082764)_

This last intuition helps, but is not perfect because many tweets are still recognised as english if they contain a part written in english, as for example

langid.classify("RT @fourmilier: #NowReading | #blogs on development and agriculture https://t.co/NqXlWFcPFC https://t.co/JSSFhiA79n;;;;;;;;")

which returns ('en', -64.45757293701172)

However this is not a big issue, because VADER dictionary assigns to this tipology of tweets 0 compound sentiment, as proven by

_RT @fourmilier: #NowReading | #blogs on development and agriculture https://t.co/NqXlWFcPFC https://t.co/JSSFhiA79n;;;;;;;; {'neg': 0.0, 'neu': 1.0, 'pos': 0.0, 'compound': 0.0}_

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
