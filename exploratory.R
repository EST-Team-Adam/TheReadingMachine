library(feather)
library(dplyr)
library(forecast)


## library(lubridate)
## check = 
##     harmonisedData %>%
##     select(., c(polarity, magnitude, date)) %>%
##     mutate(Year = year(date), Month = month(date)) %>%
##     group_by(Year, Month) %>%
##     summarise(count = n())

firstStartDate = as.Date("2011-01-01")
## NOTE (Michael): There seem to be some more problem with the
##                 extraction of the sentiment after the 'endDate',
##                 thus we currently remove those data.
endDate = as.Date("2016-04-18")
## endDate = Sys.Date()
calculateLogReturn = function(x){
    c(NA, diff(log(x)))
}

harmonisedData =
    read_feather("harmonised_data.feather") %>%
    data.frame() %>%
    mutate(date = as.Date(date, "%Y-%m-%d")) %>%
    .[order(.$date), ] %>%
    mutate(articleSentiment = magnitude * polarity)

topicVariables =
    harmonisedData %>%
    colnames %>%
    `[`(., !. %in% c("id", "date", "magnitude", "polarity"))

alpha = 0.99
filterSize = 20
revFilter = cumprod(rep(alpha, filterSize))/
    sum(cumprod(rep(alpha, filterSize)))

priceData =
    read.csv("data/igc_goi.csv", stringsAsFactors = FALSE) %>%
    mutate(date = as.Date(DATE, "%m/%d/%Y"), DATE = NULL) %>%
    mutate(wheatReturn = calculateLogReturn(Wheat),
           maizeReturn = calculateLogReturn(Maize),
           riceReturn = calculateLogReturn(Rice),
           barleyReturn = calculateLogReturn(Barley),
           soyabeansReturn = calculateLogReturn(Soyabeans)) %>%
    na.omit %>%
    subset(date > firstStartDate & date < endDate) %>%
    mutate(marketSentiment =
               c(na.omit(stats::filter(Wheat, revFilter, sides = 1)),
                 rep(NA, filterSize - 1)))

finalData =
    merge(harmonisedData, priceData, by = "date", all.y = TRUE)
    

sentimentData = 
    harmonisedData %>%
    group_by(date) %>%
    summarise(dailySentiment = sum(articleSentiment)) %>%
    ## mutate(dailySentiment =
    ##            replace(dailySentiment,
    ##                    which(is.na(dailySentiment)), 0)) %>%
    ## mutate(cumulativeSentiment = cumsum(dailySentiment)) %>%
    data.frame

plot(sentimentData)
exploratoryData = merge(sentimentData, priceData, by = "date",
                  all.y = TRUE) %>%
    mutate(dailySentiment =
               replace(dailySentiment,
                       which(is.na(dailySentiment)), 0)) %>%
    mutate(cumulativeSentiment = cumsum(dailySentiment))


jpeg(file = "market_cumulative_sentiment_correlation.jpeg",
     width = 960)
with(exploratoryData, {
     plot(marketSentiment, cumulativeSentiment)
})
graphics.off()

splitDate = as.Date("2016-01-30")
trainData =
    exploratoryData %>%
    subset(date < splitDate)
testData = 
    exploratoryData %>%
    subset(date >= splitDate)
sentimentModel =
    with(trainData, lm(marketSentiment ~ cumulativeSentiment))
summary(sentimentModel)

with(exploratoryData, plot(date, Wheat, type = "l", ylim = c(0, 400)))
with(exploratoryData, lines(date, marketSentiment, col = "green"))
with(trainData, lines(date, fitted(sentimentModel),
                      col = "steelblue"))
with(testData, lines(date, predict(sentimentModel, testData),
                     col = "steelblue", lwd = 3))
