# Commodity Market Sentiment: Capturing the Outlook of the Agriculture
  Commodity Market.


This is an interim report on the current status and future development
of the project.

## Introduction


Solving world hunger is the key responsibility of the Food and
Agricultural Organisation of the United Nations (UNFAO). This
long-term strategic goal and mission is an uncompromisable task to
achieve a better prospect of the human society.

The many dimension of this complicated issue makes it one of the most
challenging obstacle remains to be solved. Various inter-related
factors such as production, price, waste, nutrition and politics are
all important in ensuring the steady supply and distribution of food
to those who are in need.

One of the most important determinants in resolving the issue is the
stability of commodity price and ultimately the affordability of
food. In this paper, we propose a market sentiment index aiming to
capture the outlook and perception of the commodity market. This
general perception will provide a better overview of the market as
perceived by professional and traders around the world by mining the
textual information and align it with the commodity price.

A market sentiment index has several potential applications. First of
all, it provides an overview of the market not from a small group of
experts but a comprehensive aggregated views based on knowledge and
observations of professional, reporters and field analysts around the
world. Secondly, the market sentiment also has the ability to predict
the general trend of prices in the future and also the probability of
a forthcoming food crisis.

In contrast to most literature related to text mining and sentiment
analysis of financial markets, we do not focus on the predictability
of price. Price prediction based on sentiments has a very short
lifespan and generally has no predictive power more than a couple of
days. This has no application nor value to the organisation where our
goal is to ensure the long-term stability and survival of
people. Rather, our focus is on the perception of the market based on
the aggregated and continuous evolving perception of the market. The
ultimate goal is to predict potential food crisis given the current
status and future prospect of the market.

## Data

In order to make the connection between the text data in the news
articles and tweets, several preparation steps are required.

In this section, we outline the necessary steps to prepare the data in
order to perform the modelling.

### News and Tweet Scrapping

News articles are scrapped and obtained from various news
agencies. Future work includes the integration of additional news
outlet and also tweets from Twitter and StockTwits.

Standard text processing such as stemming, and removal of stopwords
were performed to transform the data into usable format. Stemming and
lemmatisation are two processes to reduce the inflected word into
their word stem. For example, running is reduced to run and cars are
reduced to car to avoid duplication of topics. Stopwords such as 'the'
are removed as they contain little if no information.

A total of 140971 of articles were obtained and processed.

### Commodity Price

Five commodities has been chosen to be the focus of this study, namely
wheat, maize, rice, barley and soybean.

The daily price of the selected commodities are obtained from the
International Grains Council (IGC).

The data spans from 2000 to 2016 with a total of 4400 daily
observations. Trading does not occur on weekends and Christmas.


## Methodology

Various steps of transformation and quantification are necessary for
the extraction of essential and relevant information contained in the
textual data.

In this section, we briefly describe each component of the project and
the current status.


### Sentiment Extraction

In order to quantify the meaning and position of each individual news
articles, a sentimental analysis is performed and each article is
scored correspondingly.

Due to the fact that sentimental analysis is highly dependent on the
financial position and the dictionary used, extensive research has
been conducted to provide a sentiment analysis toolset which meets the
need and position of the organisation.

Details of the research and analysis can be found in the [Sentence by
Sentence Sentiment
Extraction](https://github.com/EST-Team-Adam/TheReadingMachine/blob/Alberto/Sentiment_Extraction/sentence_by_sentence.pdf)
paper.

An additional set of sentiments based on the Google Natural Language
API is also extracted. This is used for comparison and benchmarking.

To capture the spread and retention of information, all sentiments are
decayed exponentially. That is, a news article will have a sentiment
score not only on the same day it was published but also all
subsequent date to represent the permanent modification of the view on
the market.

### Tagging and Topic Modelling

It would be naive to assume each piece of information as equally
relevant and has the same effect on the perception of the market. Each
article can contain information about a particular dimension such as
trade, production and research about an individual commodity. The
relevance of the piece of information with respect to the prices are
different, and thus, it is important to classify the document with
respect to the dimension.

To account for the asymmetry of the information, tagging and topic
modelling were performed to further derive additional information from
the textual data. Two dimensions of tagging were performed, adding
geographical and commodity dimension to the sentiments.

The topics are extracted based on the method non-negative matrix
factorisation. The details of the method is also outside the scope of
this overview, please refer to the [topic
modelling](https://github.com/EST-Team-Adam/TheReadingMachine/blob/mg/TopicModel/TopicModelingAMIS.ipynb)
documentation for a detailed description.

### Market State

Instead of modelling the commodity price directly, a state-space model
was fitted to the time series in order to extract the state of the
market.

The purpose of this procedure is two-fold. As we are concerned with
the long-term stability of the food prices, the fluctuation of daily
price bears little importance to the analysis. The model smoothes the
series and enables the analysis to focus solely on the level and trend
of the price. Secondly, the derived state leads the price time series,
thus, rendering predictive power to the price. If a connection can be
made between the textual information and the derived state, then we
can forecast the general trend of the price in the future.

Shown below are the price of wheat and one of the estimated
state. From the graph, we can see the state is a slow transition time
series which lead the movement of the price time series.

## Model

After deriving all possible information from the textual data, a model
is required to make the connection between the market information and
the sentiment.

The following model to estimate the effect of each individual piece of
information. The cost function is defined as follow:

``` C = sum(ms_i - y_i) = ms_i - sum(d_i * s_i) = ms_i - sum(|tw_i -
tw_hat| * s_i) ```

Where `ms_i` is the market sentiment filtered from the price series,
`tw_i` are the individual topic score of each article and `s_i` is the
sentiment of the article. The `tw_hat` are the coefficients to be
estimated, they represent the topic of the price time
series. Essentially, the `d_i` represents the relevance of the
particular dimension on the price of the commodity and the sentiments
are scaled based on the relevance.

