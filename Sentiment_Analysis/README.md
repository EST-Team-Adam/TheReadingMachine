#Sentiment Analysis#


In Sentiment_Analysis are stored scripts and paper relative to Sentence by Sentence wheat articles sentiment extraction.

Compound sentiment is extracted from sentences of a wheat articles subset using an unmodified version of VADER Analysis Tool. Such
sentiment scores are then filtered using the Kalman Filter and finally correlation between _Filtered_ _Sentiment_ and daily Wheat Price
Index is computed. The whole analysis is in the file _"Sentiment_analysis.pdf"_.

###The scripts###

The first script that has to be used is _"sentiment_extraction.py"_.

The script takes wheat articles obtained using _The Reading Machine_, selects a subset of articles where the word _"wheat"_ appears, 
extracts the sentences containing the word _"wheat"_ from each article, computes sentiment using an unmodified VADER version
and saves the results into a dataframe called _sentiment_. Such dataframe, which contains Article ID, sentences, compound sentiment and 
date, is then printed out in a csv file called _"df.csv"_.

_"df.csv"_ is in this folder because 15 observations have been manually cancelled due to format inconsistencies, namely missing dates.

Wheat articles from _The Reading Machine_ can be found at the following URL:

https://drive.google.com/file/d/0Bx88UU1MUqu0Q25NcTRoYVRoMEU/view

The second script is _"main.r"_ and its auxiliary scripts _"kalman_filter.r"_ and _"dataframe_manipulator"_.

_"main.r"_ reads _"df.csv"_ and _"igc_goi.csv"_, filters and collapse compound sentiment into daily _Filtered Sentiment_ observations and
pairs them with daily Wheat Price Index observations. In this way a not evenly spaced but contemporaneous observations dataframe is built.
Using these observations _Augmented Dickey-Fuller Tests_ are performed and correlation is computed.
