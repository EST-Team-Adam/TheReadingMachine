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

# Create reverse filter.
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


with(exploratoryData,
     plot(Wheat, cumulativeSentiment))


with(exploratoryData,
     plot(lowess(Wheat ~ date)$y,
          lowess(cumulativeSentiment ~ date)$y))


with(exploratoryData,
     plot(marketSentiment, cumulativeSentiment))

with(exploratoryData,
     plot(diff(marketSentiment), diff(cumulativeSentiment)))


with(exploratoryData,{
     plot(date, scale(marketSentiment), type = "l", col = "red")
     lines(date, scale(cumulativeSentiment))})

with(exploratoryData,{
    plot(date, scale(lowess(Wheat ~ date)$y),
         type = "l", col = "red")
    lines(date, scale(lowess(cumulativeSentiment ~ date)$y))})


runCor = function(x, y, window = 30){
    totalIter = length(x) - window + 1
    runCorrelation = vector("numeric", totalIter)
    for(i in 1:totalIter){
        index = (0 + i):(window + i - 1)
        runCorrelation[i] = cor(x[index], y[index])
    }
    runCorrelation
}

## The running correlation exhibit oscilation between +/-1. This
## suggest model such as auto-correlation may not perform well.
rc = with(exploratoryData,
          runCor(marketSentiment, cumulativeSentiment, window = 30))
plot(rc, type = "l")



sp = 0.3
exploratoryData$smoothedWheat =
    with(exploratoryData, lowess(Wheat ~ date, f = sp)$y)

exploratoryData$smoothedSentiment =
    with(exploratoryData, lowess(cumulativeSentiment ~ date, f = sp)$y)

with(exploratoryData, plot(smoothedWheat, smoothedSentiment))

rcSmoothed = with(exploratoryData,
          runCor(smoothedWheat, smoothedSentiment, window = 30))
plot(rcSmoothed, type = "l", ylim = c(-1, 1))



########################################################################
## Model
########################################################################

topicScore = harmonisedData[, 7:106]
topicSentiment = topicScore * harmonisedData$articleSentiment

weightedSentiment = cbind(date = harmonisedData[, c("date")],
                          topicSentiment)

summedSentiment =
    weightedSentiment %>%
    group_by(date) %>%
    summarise_each(funs(sum)) %>%
    subset(., select = -date) %>%
    cumsum %>%
    ## sweep(., 1, rowSums(.), FUN = "/") %>%
    cbind(date = unique(weightedSentiment$date), .)


## TODO (Michael): Need to smooth both series, the plots above shows
##                 that smoothed time series has a very high
##                 correlation.
priceData$smoothed =
    with(priceData, lowess(IGC.GOI ~ date, f = 0.1)$y)

    


var = "smoothed"
wheatModel.df =
    merge(priceData[, c("date", var)],
    ## merge(priceData[, c("date", "marketSentiment")],
          summedSentiment, all.x = TRUE, by = "date") %>%
    ## NOTE (Michael): There seem to be problem with data prior to 2013.
    ## subset(., date > as.Date("2013-01-01")) %>%
    na.omit



## pdf(file = "check.pdf")
## for(i in 2:NCOL(wheatModel.df)){
##     plot(wheatModel.df[, 1], wheatModel.df[, i], type = "l",
##          xlab = colnames(wheatModel.df)[i])
## }
## graphics.off()

library(glmnet)
wheatModel = 
    wheatModel.df %>%
    ## subset(., select = -date) %>%
    subset(., select = -date, date < as.Date("2013-01-01")) %>%
    ## subset(., select = -date, date > as.Date("2015-01-01")) %>%
    ## subset(., select = -date,
    ##        date < as.Date("2015-06-01") &
    ##        date > as.Date("2013-06-01")) %>%
    {
        xvars = as.matrix(.[, -1])
        yvar = as.matrix(.[, 1])
        cv.glmnet(xvars, yvar)
    }

modelCoef = coef(wheatModel, s = "lambda.min")
predicted = cbind(1, as.matrix(wheatModel.df[, -c(1, 2)])) %*%
    as.matrix(modelCoef)




with(wheatModel.df,
{
    ## plot(date, Wheat, type = "l", ylim = c(0, 350))
    ## plot(date, wheatModel.df[, var], type = "l", ylim = c(0, 550))
    plot(date, wheatModel.df[, var], type = "l", ylim = c(150, 350))    
    ## plot(date, marketSentiment, type = "l", ylim = c(0, 350))
    lines(date, predicted, col = "red")
})


########################################################################







with(exploratoryData,
     cor(marketSentiment, cumulativeSentiment,
         use = "pairwise.complete.obs"))


with(exploratoryData,
     cor(marketSentiment, Wheat,
         use = "pairwise.complete.obs"))



alpha = 0.99
filterSize = 120
revFilter = cumprod(rep(alpha, n))/sum(cumprod(rep(alpha, n)))

reverseFiltering = function(alpha, filterSize, series){
    revFilter =
        cumprod(rep(alpha, filterSize))/
        sum(cumprod(rep(alpha, filterSize)))
    c(na.omit(stats::filter(series, revFilter, sides = 1)),
      rep(NA, filterSize - 1))
}

    
foo = function(par, sentimentSeries, priceSeries){
    print(par)
    filteredPriceSeries =
        reverseFiltering(par[1], par[2], priceSeries)
    correlation = cor(filteredPriceSeries, sentimentSeries,
                      use = "pairwise.complete.obs")
    print(correlation)
    correlation
}

optim(par = c(0.5, 10),
      f = foo,
      lower = c(0.1, 2),
      upper = c(1, 365),
      priceSeries = finalData$Wheat,
      sentimentSeries = finalData$cumulativeSentiment)

foo(c(alpha, filterSize),
    priceSeries = finalData$Wheat,
    sentimentSeries = finalData$cumulativeSentiment)

plot(finalData$Wheat)
lines(reverseFiltering(0.1, 90, finalData$Wheat), col = "red")

with(finalData, {
    plot(date, Wheat, type = "l")
    lines(date, cumulativeSentiment + 20403, col = "red")
})


## subData = finalData[finalData$date >= as.Date("2015-01-01"), ]
## write_feather(subData, "analysis_data.feather")


## topicAggregated =
##     harmonisedData %>%
##     select(., -id) %>%
##     group_by(date) %>%
##     summarise_each(funs(mean))

## topicVariables =
##     topicAggregated %>%
##     colnames %>%
##     `[`(., . != "date")

## finalData =
##     merge(harmonisedData, priceData, all.y = TRUE) %>%
##     subset(date > as.Date("2010-01-01"))
finalData[is.na(finalData)] = 0



costFun = function(param, topicMatrix, individualSentiment,
                   marketSentiment, dateIndex){
    ## d = sweep(t(topicMatrix), 1, param)
    d = t(t(topicMatrix) - param)
    distance = apply(d, 1, FUN = function(x) sqrt(sum(x^2)))
    fittedSentiment = c(by(distance * individualSentiment,
                           dateIndex, sum))
    ## print(head(fittedSentiment, 100))
    correlation = cor(fittedSentiment, marketSentiment,
                      use = "pairwise.complete.obs")
    print(correlation)
    -abs(correlation)
}

topicMatrix = scale(as.matrix(finalData[, topicVariables]))
individualSentiment = finalData$individualSentiment
marketSentiment = c(NA, diff(priceData$marketSentiment))
dateIndex = finalData$date

myControl = list(maxit = 10, ndeps = 1e-2)
fit =  optim(par = colMeans(topicMatrix),
## fit =  optim(par = rnorm(ncol(topicMatrix)),
             fn = costFun,
             topicMatrix = topicMatrix,
             individualSentiment = individualSentiment,
             marketSentiment = marketSentiment,
             dateIndex = dateIndex,
             control = myControl)

topicPredict = function(topicMatrix, topicCenter,
                        individualSentiment,
                        marketSentiment, dateIndex){
    d = t(t(topicMatrix) - topicCenter)
    distance = apply(d, 1, FUN = function(x) sqrt(sum(x^2)))
    fittedSentiment = c(by(distance * individualSentiment,
                           dateIndex, sum))
    fittedSentiment
}

fitted = topicPredict(topicMatrix,
                      fit$par,
                      individualSentiment,
                      marketSentiment,
                      dateIndex)

scaledFitted = (fitted - mean(fitted))/(sd(fitted)/5) + 250

with(priceData,
     {
         plot(date, Wheat, type = "l")
         lines(date, cumsum(scaledFitted))
     })



sumFitted = cumsum(fitted - mean(fitted))/(sd(fitted))

with(priceData,
{
    par(mfrow = c(2, 1))
         plot(date, Wheat, type = "l")
         plot(date, sumFitted)
     })

plot(priceData$Wheat, sumFitted)

pdf(file = "coef.pdf")
for(i in colnames(finalData)){
    plot(finalData[, i], main = i, type = "h")
}
graphics.off()


marketSentimentFitted =
    cumsum(c(by(individualSentiment, dateIndex, sum)))

with(priceData,
{
    par(mfrow = c(2, 1))
         plot(date, Wheat, type = "l")
         plot(date, marketSentimentFitted, type = "l")
     })

plot(priceData$Wheat, marketSentimentFitted)
plot(priceData$marketSentiment, marketSentimentFitted)    



#####################################################################

jpeg(file = "market_state.jpg", width = 960)
plot(testtime, testts, type = "l", xlab = "", ylab = "")
lines(testtime, testfts, col = "red")
legend("topleft", legend = c("Daily Wheat Price", "Market State"),
       col = c("black", "red"), lty = 1, bty = "n")
graphics.off()

pdf(file = "test.pdf")
for(i in colnames(finalData)){
    par(mfrow = c(4, 1))
    plot(unlist(finalData["date"]),
         unlist(finalData[, i]), type = "l",
         main = i)
    plot(unlist(finalData["date"]),
         unlist(abs(finalData["wheatReturn"])), type = "l")
    plot(unlist(finalData[, i]),
         unlist(abs(finalData["wheatReturn"])))
    ccf(unlist(finalData[, i]),
        unlist(abs(finalData["wheatReturn"])), lag.max = 30)
}
graphics.off()


## 1. sum each topic score by date
##
## 2. Merge with wheat price and subset out duration where there isn't
##    much article data.
##
## 3. Create exponential smoothing of the relevancy.
##
## 4. Calculate absolute price changes.
##
## 5. Conduct correlation analysis.

## TODO (Michael): Need to match news on non-trading dates to the
##                 following trading date.
    
