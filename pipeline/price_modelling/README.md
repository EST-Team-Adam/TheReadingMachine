# Price Modelling

This module harmonises all the information extracted and processed to
provide a robust and accurate prediction of the trend of commodity
prices.

## Response

First of all, the price data is smoothed using seasonal decomposition
by LOESS. The trend of the decomposition is extracted as response.

The reason for this smoothing is because we want to predict the trend
and not influenced by the daily fluctuation in the daily prices.

## Sentiment processing

In order to incorporate the sentiment of the articles, the sentiment
is aggregated by topic by date, then a cumulative sum is taken.

The use of cumulative sum instead of typical exponential smoothing or
decay model is because the sentiment is used as a proxy for the
perception of the market. We want to retain the property such that
even in the state where there are no new news publication, the
perception is unchanged rather than decay to some arbitrary level.

We also smoothed the sentiment to smooth out the daily fluctuation.

## Model

Several model has been attempted. A benchmark using simple linear
regression has been devised as the benchmark.


