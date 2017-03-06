#Sentence Selector#

The script, which is based on Sentence Topics, extracts each sentence main topics and extracts relevant sentences 
for any given named entity. In particular Sentence Topics extracts each sentence main topics (namely the Noun Phrases) in the form 
of a set of keywords, therefore Sentence Selector checks if a set of given words are present in the extracted topics. 
If the given word is present, the sentence is properly formatted (namely cleaned from a few special characters), then 
it's analysed using VADER sentiment analysis tool and Google NLP and the result is stored in a list.
The final output is a JSON file per each named entity, in this version _wheat_, _soybeans_ and _maize_, which contains sentences, sentiment
scores, article id and dates.

## The script ##
The main script is _selector_POC.py_ is the main file which loads the articles stored in _amis_articles_27_11_2016_indexed.jsonl_,
takes a random sample of 1000 articles, (arbitrarily) defines the keywords of interest, calls the _sentences_analyzer_ and stores the 
results in the JSON files.

The _sentences_analyzer_ function is contained into _sentence_selector.py_. The function relies on the Sentence Boundaries Definition
 script (_SBD.py_), the sentence topic extraction script (_sentence_keywords_), NLTK stemmer and stop-words and VADER and Google NLP
sentiment analyzers. Lines 29-30 can be modified to reintroduce Google NLP (which has been disabled due to computation time).

The function takes each article and divides it into sentences using the SBD and, while defining the sentences, a function contained in
_textcleaner.py_ cleans the text from special characters and other problematic format issues. Each sentence is then analyzed using the 
Sentence Topic Extractor and a function called _keyword_alarm_ checks if the extracted extracted topic keywords match the given keywords
for the arbitrarily given entities. For this step each keyword, both topic-extracted and aribitrarily given, is stemmed and removed of
any (eventual) stopword: this step is necessary to decrease the number of missed matches due to the text format. (Given this procedure
the script is robust also to whole phrases given as aribitrary named entities)

When a match is highlighted by _keyword_alarm_ function, the sentence cleaned version is stored and it's analysed using both
VADER and Google NLP. The results are then stored and dumped in a JSON file.

## The Output ##

The output is a json file which contains per each sentence its date, article id, the same sentence, all _negative_, _positive_, 
_neutral_ and _compound_ sentiment from VADER and both _polarity_ and _magnitude_ from Google NLP (if re-activated).

The current version extracts 11900 _wheat_, 3059 _soybeans_ and 583 _maize_ related sentences from the whole articles corpus.
Since the computation takes a long time, the files are at the following link:
https://drive.google.com/open?id=0Bx88UU1MUqu0OHBsYTBNd3RsRDQ

## Next Research Topics ##

At the moment new sentiment scores have still to be analysed and compared with old ones, therefore the main focus will be to run
the old analysis using the new scores and underline eventual differences. Moreover VADER extracted sentiment will be compared to
Google NLP sentiment.

Another issue  involves _rice_ because this word is used both as commodity name and
Proper Noun (exactly a surname). Unfortunately the Sentence Selector doesn't know the difference between rice as commodity and
a person named Rice, therefore it extracts also the sentences related to people. This issue will be solved.

By changing the Context Free Grammar will change also the extracted Noun Phrases since the whole Sentence Selector is based on 
the sentence topics extraction, therefore new CFG configurations will be tried if the results will be unsatisfactory.

Residually it will be checked if the text cleaning mechanism sufficiently cleans the text into a satisfactory format. If new 
format issue will be found, they'll be added to the list into _textcleaner.py_ for removal.
